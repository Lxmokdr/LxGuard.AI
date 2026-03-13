import os
import logging
from typing import List, Dict, Optional, Any, Union
from dataclasses import dataclass, asdict
import shutil
from datetime import datetime
import re
import json

# Initialize logger
logger = logging.getLogger("RuleManager")

@dataclass
class RuleDefinition:
    id: str
    description: str = ""
    priority: int = 5
    intent: str = "General"
    enabled: bool = True
    conditions: List[Dict[str, Any]] = None # Structured conditions
    actions: Dict[str, Any] = None # Structured actions
    dsl_content: str = "" # Keep raw DSL for display

class DSLParser:
    """
    Robust State-Machine Parser for the Expert Rule DSL.
    Parses human-readable rules into structured JSON-compatible objects.
    """
    def __init__(self):
        self.rules = []
        self.current_rule = None
        self.state = "IDLE" # IDLE, IN_RULE, IN_WHEN, IN_THEN

    def parse(self, text: str) -> List[Dict[str, Any]]:
        self.rules = []
        self.current_rule = None
        self.state = "IDLE"
        
        lines = text.splitlines()
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
                
            self._process_line(line, line_num)
            
        # Add the last rule
        if self.current_rule:
            self.rules.append(self.current_rule)
            
        return self.rules

    def _process_line(self, line: str, line_num: int):
        # 1. Detect Rule Start
        rule_match = re.match(r'RULE\s+"(.*?)"', line)
        if rule_match:
            if self.current_rule:
                self.rules.append(self.current_rule)
            
            self.current_rule = {
                "id": rule_match.group(1),
                "priority": 5, # default
                "enabled": True,
                "description": "",
                "intent": "General", # default
                "conditions": {},
                "actions": {},
                "raw_lines": [line]
            }
            self.state = "IN_RULE"
            return

        if not self.current_rule:
             return # Skip lines outside a rule block

        self.current_rule["raw_lines"].append(line)

        # 2. State Transitions
        if line == "WHEN":
            self.state = "IN_WHEN"
            return
        elif line == "THEN":
            self.state = "IN_THEN"
            return

        # 3. Parsing based on State
        if self.state == "IN_RULE":
            # Parse Metadata
            if line.startswith("PRIORITY"):
                try:
                    self.current_rule["priority"] = int(line.split(":")[1].strip())
                except:
                    pass
            elif line.startswith("DESCRIPTION"):
                self.current_rule["description"] = line.split(":")[1].strip().strip('"')
            elif line.startswith("DISABLED"):
                 self.current_rule["enabled"] = False
            elif line.startswith("VERSION"):
                self.current_rule["version"] = line.split(":")[1].strip().strip('"')

        elif self.state == "IN_WHEN":
            # Parse Conditions
            # intent IS "Deployment"
            intent_match = re.match(r'intent\s+IS\s+"(.*?)"', line)
            if intent_match:
                self.current_rule["intent"] = intent_match.group(1)
            
            # user.role IN ["guest", "admin"]
            role_match = re.match(r'user\.role\s+IN\s+\[(.*?)\]', line)
            if role_match:
                roles = [r.strip().strip('"').strip("'") for r in role_match.group(1).split(',')]
                self.current_rule["conditions"]["user_role"] = roles

            # user.role IS "guest"
            role_is_match = re.match(r'user\.role\s+IS\s+"(.*?)"', line)
            if role_is_match:
                self.current_rule["conditions"]["user_role"] = [role_is_match.group(1)]

        elif self.state == "IN_THEN":
            # Parse Actions
            # FORBID documents: ["doc1", "doc2"]
            forbid_match = re.match(r'FORBID\s+documents:\s+\[(.*?)\]', line)
            if forbid_match:
                docs = [d.strip().strip('"').strip("'") for d in forbid_match.group(1).split(',')]
                self.current_rule["actions"]["forbid_documents"] = docs
            
            # EXCLUDE intents: ["Intent1"]
            exclude_match = re.match(r'EXCLUDE\s+intents:\s+\[(.*?)\]', line)
            if exclude_match:
                intents = [i.strip().strip('"').strip("'") for i in exclude_match.group(1).split(',')]
                self.current_rule["actions"]["exclude_intents"] = intents
                
            # MAX_LENGTH: 100
            length_match = re.match(r'MAX_LENGTH:\s+(\d+)', line)
            if length_match:
                self.current_rule["actions"]["max_length"] = int(length_match.group(1))

class RuleManager:
    """
    Manages the lifecycle of Expert Rules (DSL).
    Handles persistence to disk (config/rules.dsl) and compilation.
    """
    def __init__(self, config_dir: str = "config"):
        self.config_dir = config_dir
        self.rules_file = os.path.join(config_dir, "rules.dsl")
        self.parser = DSLParser()
        self._ensure_config_dir()

    def _ensure_config_dir(self):
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        # Create empty rules file if not exists
        if not os.path.exists(self.rules_file):
            with open(self.rules_file, "w") as f:
                f.write("# Expert Logic Rules (DSL)\n# Auto-generated by RuleManager\n")

    def load_rules(self) -> List[Dict[str, Any]]:
        """
        Parses the DSL file using the Robust State Machine Parser.
        """
        if not os.path.exists(self.rules_file):
            return []

        try:
            with open(self.rules_file, "r") as f:
                content = f.read()
            
            parsed_rules = self.parser.parse(content)
            
            # Hydrate into format expected by API
            rules = []
            for r in parsed_rules:
                rules.append({
                    "id": r["id"],
                    "description": r.get("description", ""),
                    "priority": r.get("priority", 5),
                    "enabled": r.get("enabled", True),
                    "intent": r.get("intent", "General"),
                    "dsl_content": "\n".join(r["raw_lines"])
                })
            return rules
                
        except Exception as e:
            logger.error(f"Failed to load rules: {e}")
            return []

    def save_rule(self, rule_data: Dict[str, Any]) -> bool:
        """
        Saves or updates a rule in the DSL file.
        Re-writes the file to ensure consistency.
        """
        try:
            current_rules = self.load_rules()
            
            # Update or Append
            existing_idx = next((i for i, r in enumerate(current_rules) if r["id"] == rule_data["id"]), -1)
            
            dsl_content = self._format_rule_dsl(rule_data)
            
            new_rule_entry = {
                "id": rule_data["id"],
                "description": rule_data.get("description", ""),
                "priority": rule_data.get("priority", 5),
                "enabled": rule_data.get("enabled", True),
                "intent": rule_data.get("intent", "General"),
                "dsl_content": dsl_content
            }
            
            if existing_idx >= 0:
                current_rules[existing_idx] = new_rule_entry
            else:
                current_rules.append(new_rule_entry)
            
            # Write back to file
            with open(self.rules_file, "w") as f:
                f.write(f"# Expert Logic Rules (DSL)\n# Last Updated: {datetime.now()}\n\n")
                for r in current_rules:
                    f.write(r["dsl_content"] + "\n\n")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to save rule: {e}")
            return False

    def delete_rule(self, rule_id: str) -> bool:
        """
        Removes a rule from the DSL file.
        """
        try:
            current_rules = self.load_rules()
            filtered_rules = [r for r in current_rules if r["id"] != rule_id]
            
            if len(current_rules) == len(filtered_rules):
                return False # Not found
            
            with open(self.rules_file, "w") as f:
                f.write(f"# Expert Logic Rules (DSL)\n# Last Updated: {datetime.now()}\n\n")
                for r in filtered_rules:
                    f.write(r["dsl_content"] + "\n\n")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete rule: {e}")
            return False

    def _format_rule_dsl(self, rule: Dict[str, Any]) -> str:
        """
        Formats a rule object into DSL syntax.
        """
        # If complete DSL content is provided, use it (for updates that don't change logic)
        # But we must check if it's the right ID to key injection
        dsl_raw = rule.get("dsl_content", "")
        if dsl_raw and f'RULE "{rule["id"]}"' in dsl_raw:
             return dsl_raw.strip()

        # Otherwise construct it
        priority = rule.get("priority", 5)
        description = rule.get("description", "Custom Rule")
        intent = rule.get("intent", "General")
        
        lines = [
            f'RULE "{rule["id"]}"',
            f'  PRIORITY: {priority}',
            f'  DESCRIPTION: "{description}"'
        ]
        
        if not rule.get("enabled", True):
             lines.append('  DISABLED')
             
        lines.append('')
        lines.append('  WHEN')
        lines.append(f'    intent IS "{intent}"')
        
        lines.append('')
        lines.append('  THEN')
        lines.append('    ALLOW')
        
        return "\n".join(lines)
