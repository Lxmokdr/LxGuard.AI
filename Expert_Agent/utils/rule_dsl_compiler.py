"""
Rule DSL Compiler - Compiles human-readable DSL to internal rule format
Responsibilities:
- Parse DSL syntax
- Validate rules (semantic, RBAC, conflicts)
- Detect unreachable rules
- Generate optimized rule representation
- Provide detailed error reporting

This ensures RULE QUALITY and CONSISTENCY.
"""

import re
import yaml
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CompilationError:
    """Represents a compilation error or warning"""
    line_number: int
    error_type: str  # 'syntax', 'semantic', 'conflict', 'warning'
    message: str
    suggestion: Optional[str] = None


@dataclass
class ParsedRule:
    """Intermediate representation of a parsed rule"""
    name: str
    version: str
    priority: int
    description: str
    conditions: Dict[str, Any]
    actions: Dict[str, Any]
    conflicts_with: List[str]
    supersedes: List[str]
    line_number: int


class RuleDSLCompiler:
    """
    Rule DSL Compiler - Converts human-readable DSL to validated rules.
    Performs syntax checking, semantic validation, and conflict detection.
    """
    
    def __init__(self, ontology_path: str = "config/intent_ontology.json"):
        self.ontology_path = Path(ontology_path)
        self.valid_intents = self._load_valid_intents()
        self.valid_roles = ["admin", "employee", "guest"]
        self.valid_structures = ["step_by_step", "conceptual_then_example", "example_driven", "reference", "flexible"]
        self.errors: List[CompilationError] = []
        self.warnings: List[CompilationError] = []
        print("🔧 Rule DSL Compiler initialized")
    
    def _load_valid_intents(self) -> List[str]:
        """Load valid intent names from ontology"""
        try:
            import json
            with open(self.ontology_path, 'r') as f:
                ontology = json.load(f)
                return [intent["name"] for intent in ontology.get("intents", [])]
        except Exception as e:
            print(f"⚠️  Could not load ontology: {e}")
            return []
    
    def compile_file(self, dsl_path: str) -> Tuple[List[Dict[str, Any]], List[CompilationError]]:
        """
        Compile a DSL file to internal rule format.
        Returns: (compiled_rules, errors)
        """
        self.errors = []
        self.warnings = []
        
        try:
            with open(dsl_path, 'r') as f:
                content = f.read()
        except FileNotFoundError:
            self.errors.append(CompilationError(
                line_number=0,
                error_type='file',
                message=f"File not found: {dsl_path}"
            ))
            return [], self.errors
        
        # Split into individual rules (separated by ---)
        rule_blocks = content.split('---')
        parsed_rules = []
        
        for i, block in enumerate(rule_blocks):
            block = block.strip()
            if not block:
                continue
            
            parsed_rule = self._parse_rule_block(block, i)
            if parsed_rule:
                parsed_rules.append(parsed_rule)
        
        # Validate all rules
        self._validate_rules(parsed_rules)
        
        # Detect conflicts
        self._detect_conflicts(parsed_rules)
        
        # Convert to internal format if no critical errors
        if not any(e.error_type in ['syntax', 'semantic'] for e in self.errors):
            compiled_rules = [self._to_internal_format(r) for r in parsed_rules]
            return compiled_rules, self.errors + self.warnings
        
        return [], self.errors + self.warnings
    
    def _parse_rule_block(self, block: str, block_index: int) -> Optional[ParsedRule]:
        """Parse a single rule block"""
        lines = block.split('\n')
        current_line = block_index * 20  # Approximate line number
        
        # Extract rule name
        rule_match = re.match(r'RULE\s+"([^"]+)"', lines[0])
        if not rule_match:
            self.errors.append(CompilationError(
                line_number=current_line,
                error_type='syntax',
                message="Rule must start with RULE \"<name>\"",
                suggestion="Use format: RULE \"My Rule Name\""
            ))
            return None
        
        rule_name = rule_match.group(1)
        
        # Initialize rule components
        version = "1.0.0"
        priority = 5
        description = ""
        conditions = {}
        actions = {}
        conflicts_with = []
        supersedes = []
        
        # Parse metadata and blocks
        current_section = None
        condition_lines = []
        action_lines = []
        
        for i, line in enumerate(lines[1:], start=1):
            line = line.strip()
            if not line:
                continue
            
            # Metadata
            if line.startswith("VERSION:"):
                version = line.split(":", 1)[1].strip().strip('"')
            elif line.startswith("PRIORITY:"):
                try:
                    priority = int(line.split(":", 1)[1].strip())
                    if not 1 <= priority <= 10:
                        self.warnings.append(CompilationError(
                            line_number=current_line + i,
                            error_type='warning',
                            message=f"Priority {priority} outside recommended range 1-10"
                        ))
                except ValueError:
                    self.errors.append(CompilationError(
                        line_number=current_line + i,
                        error_type='syntax',
                        message="Priority must be an integer"
                    ))
            elif line.startswith("DESCRIPTION:"):
                description = line.split(":", 1)[1].strip().strip('"')
            elif line.startswith("CONFLICTS_WITH:"):
                conflicts_str = line.split(":", 1)[1].strip()
                conflicts_with = self._parse_list(conflicts_str)
            elif line.startswith("SUPERSEDES:"):
                supersedes_str = line.split(":", 1)[1].strip()
                supersedes = self._parse_list(supersedes_str)
            
            # Section markers
            elif line == "WHEN":
                current_section = "when"
            elif line == "THEN":
                current_section = "then"
            
            # Section content
            elif current_section == "when":
                condition_lines.append(line)
            elif current_section == "then":
                action_lines.append(line)
        
        # Parse conditions
        conditions = self._parse_conditions(condition_lines, current_line)
        
        # Parse actions
        actions = self._parse_actions(action_lines, current_line)
        
        return ParsedRule(
            name=rule_name,
            version=version,
            priority=priority,
            description=description,
            conditions=conditions,
            actions=actions,
            conflicts_with=conflicts_with,
            supersedes=supersedes,
            line_number=current_line
        )
    
    def _parse_list(self, list_str: str) -> List[str]:
        """Parse a list from DSL format: [item1, item2, item3]"""
        list_str = list_str.strip()
        if list_str.startswith('[') and list_str.endswith(']'):
            list_str = list_str[1:-1]
        
        items = [item.strip().strip('"').strip("'") for item in list_str.split(',')]
        return [item for item in items if item]
    
    def _parse_conditions(self, lines: List[str], base_line: int) -> Dict[str, Any]:
        """Parse WHEN block conditions"""
        conditions = {}
        
        for line in lines:
            # intent IS "IntentName"
            intent_match = re.match(r'intent\s+IS\s+"([^"]+)"', line)
            if intent_match:
                intent = intent_match.group(1)
                conditions['intent'] = intent
                
                # Validate intent
                if self.valid_intents and intent not in self.valid_intents:
                    similar = self._find_similar(intent, self.valid_intents)
                    self.errors.append(CompilationError(
                        line_number=base_line,
                        error_type='semantic',
                        message=f"Invalid intent: '{intent}'",
                        suggestion=f"Did you mean: {similar}?" if similar else None
                    ))
            
            # user.role IN [roles]
            role_match = re.match(r'user\.role\s+IN\s+\[([^\]]+)\]', line)
            if role_match:
                roles_str = role_match.group(1)
                roles = self._parse_list(f"[{roles_str}]")
                conditions['allowed_roles'] = roles
                
                # Validate roles
                for role in roles:
                    if role not in self.valid_roles:
                        self.errors.append(CompilationError(
                            line_number=base_line,
                            error_type='semantic',
                            message=f"Invalid role: '{role}'",
                            suggestion=f"Valid roles: {', '.join(self.valid_roles)}"
                        ))
        
        return conditions
    
    def _parse_actions(self, lines: List[str], base_line: int) -> Dict[str, Any]:
        """Parse THEN block actions"""
        actions = {}
        
        for line in lines:
            # ALLOW documents: [docs]
            if line.startswith("ALLOW documents:"):
                docs_str = line.split(":", 1)[1].strip()
                actions['required_docs'] = self._parse_list(docs_str)
            
            # FORBID documents: [docs]
            elif line.startswith("FORBID documents:"):
                docs_str = line.split(":", 1)[1].strip()
                actions['forbidden_docs'] = self._parse_list(docs_str)
            
            # STRUCTURE: type
            elif line.startswith("STRUCTURE:"):
                structure = line.split(":", 1)[1].strip()
                if structure not in self.valid_structures:
                    self.warnings.append(CompilationError(
                        line_number=base_line,
                        error_type='warning',
                        message=f"Unknown structure type: '{structure}'",
                        suggestion=f"Valid types: {', '.join(self.valid_structures)}"
                    ))
                actions['answer_structure'] = structure
            
            # EXCLUDE intents: [intents]
            elif line.startswith("EXCLUDE intents:"):
                intents_str = line.split(":", 1)[1].strip()
                actions['excluded_intents'] = self._parse_list(intents_str)
            
            # REQUIRE citations: bool
            elif line.startswith("REQUIRE citations:"):
                value = line.split(":", 1)[1].strip().lower()
                actions['require_citations'] = value == 'true'
            
            # MAX_LENGTH: number
            elif line.startswith("MAX_LENGTH:"):
                try:
                    length = int(line.split(":", 1)[1].strip())
                    actions['max_length'] = length
                except ValueError:
                    self.errors.append(CompilationError(
                        line_number=base_line,
                        error_type='syntax',
                        message="MAX_LENGTH must be an integer"
                    ))
        
        return actions
    
    def _validate_rules(self, rules: List[ParsedRule]):
        """Validate all rules for semantic correctness"""
        rule_names = set()
        
        for rule in rules:
            # Check for duplicate names
            if rule.name in rule_names:
                self.errors.append(CompilationError(
                    line_number=rule.line_number,
                    error_type='semantic',
                    message=f"Duplicate rule name: '{rule.name}'",
                    suggestion="Rule names must be unique"
                ))
            rule_names.add(rule.name)
            
            # Validate version format
            if not re.match(r'^\d+\.\d+\.\d+$', rule.version):
                self.warnings.append(CompilationError(
                    line_number=rule.line_number,
                    error_type='warning',
                    message=f"Invalid version format: '{rule.version}'",
                    suggestion="Use semantic versioning: X.Y.Z"
                ))
            
            # Check for document conflicts (same doc in ALLOW and FORBID)
            required = set(rule.actions.get('required_docs', []))
            forbidden = set(rule.actions.get('forbidden_docs', []))
            conflicts = required & forbidden
            if conflicts:
                self.errors.append(CompilationError(
                    line_number=rule.line_number,
                    error_type='semantic',
                    message=f"Document appears in both ALLOW and FORBID: {conflicts}",
                    suggestion="Remove from one list"
                ))
    
    def _detect_conflicts(self, rules: List[ParsedRule]):
        """Detect conflicts between rules"""
        # Group rules by intent
        by_intent: Dict[str, List[ParsedRule]] = {}
        for rule in rules:
            intent = rule.conditions.get('intent', 'Unknown')
            if intent not in by_intent:
                by_intent[intent] = []
            by_intent[intent].append(rule)
        
        # Check for conflicts within same intent
        for intent, intent_rules in by_intent.items():
            if len(intent_rules) > 1:
                # Check for same priority
                priorities = {}
                for rule in intent_rules:
                    if rule.priority in priorities:
                        self.warnings.append(CompilationError(
                            line_number=rule.line_number,
                            error_type='conflict',
                            message=f"Rules '{rule.name}' and '{priorities[rule.priority]}' have same priority for intent '{intent}'",
                            suggestion="Adjust priority to establish clear precedence"
                        ))
                    priorities[rule.priority] = rule.name
                
                # Check for contradictory RBAC
                for i, rule_a in enumerate(intent_rules):
                    for rule_b in intent_rules[i+1:]:
                        roles_a = set(rule_a.conditions.get('allowed_roles', []))
                        roles_b = set(rule_b.conditions.get('allowed_roles', []))
                        
                        if roles_a and roles_b and roles_a & roles_b:
                            # Overlapping roles - check for contradictions
                            docs_a = set(rule_a.actions.get('required_docs', []))
                            docs_b = set(rule_b.actions.get('required_docs', []))
                            
                            if docs_a and docs_b and not (docs_a & docs_b):
                                self.warnings.append(CompilationError(
                                    line_number=rule_a.line_number,
                                    error_type='conflict',
                                    message=f"Rules '{rule_a.name}' and '{rule_b.name}' have overlapping roles but different document requirements",
                                    suggestion="Consider merging or clarifying role separation"
                                ))
        
        # Check explicit conflicts
        for rule in rules:
            for conflict_name in rule.conflicts_with:
                # Find the conflicting rule
                conflicting_rule = next((r for r in rules if r.name == conflict_name), None)
                if not conflicting_rule:
                    self.warnings.append(CompilationError(
                        line_number=rule.line_number,
                        error_type='warning',
                        message=f"CONFLICTS_WITH references unknown rule: '{conflict_name}'"
                    ))
    
    def _to_internal_format(self, rule: ParsedRule) -> Dict[str, Any]:
        """Convert parsed rule to internal YAML-compatible format"""
        internal = {
            "id": rule.name.upper().replace(" ", "_"),
            "triggers": [rule.conditions.get('intent', 'General')],
            "priority": rule.priority,
            "description": rule.description,
            "version": rule.version,
            "action": {
                "topic": rule.conditions.get('intent', 'general').lower(),
                **rule.actions
            }
        }
        
        # Add allowed roles if specified
        if 'allowed_roles' in rule.conditions:
            internal['allowed_roles'] = rule.conditions['allowed_roles']
        
        # Add excludes
        if 'excluded_intents' in rule.actions:
            internal['excludes'] = rule.actions['excluded_intents']
        
        return internal
    
    def _find_similar(self, word: str, candidates: List[str]) -> Optional[str]:
        """Find similar word using simple edit distance"""
        def levenshtein(s1: str, s2: str) -> int:
            if len(s1) < len(s2):
                return levenshtein(s2, s1)
            if len(s2) == 0:
                return len(s1)
            
            previous_row = range(len(s2) + 1)
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row
            
            return previous_row[-1]
        
        best_match = None
        best_distance = float('inf')
        
        for candidate in candidates:
            distance = levenshtein(word.lower(), candidate.lower())
            if distance < best_distance and distance <= 3:
                best_distance = distance
                best_match = candidate
        
        return best_match
    
    def format_errors(self) -> str:
        """Format errors and warnings for display"""
        output = []
        
        if self.errors:
            output.append("❌ ERRORS:")
            for error in self.errors:
                output.append(f"  [Line {error.line_number}] {error.error_type.upper()}: {error.message}")
                if error.suggestion:
                    output.append(f"    💡 {error.suggestion}")
        
        if self.warnings:
            output.append("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                output.append(f"  [Line {warning.line_number}] {warning.message}")
                if warning.suggestion:
                    output.append(f"    💡 {warning.suggestion}")
        
        return "\n".join(output) if output else "✅ No errors or warnings"


# CLI Interface
if __name__ == "__main__":
    import sys
    import json
    
    compiler = RuleDSLCompiler()
    
    if len(sys.argv) < 2:
        print("Usage: python rule_dsl_compiler.py <dsl_file> [--output <yaml_file>]")
        sys.exit(1)
    
    dsl_file = sys.argv[1]
    output_file = None
    
    if "--output" in sys.argv:
        output_index = sys.argv.index("--output")
        if output_index + 1 < len(sys.argv):
            output_file = sys.argv[output_index + 1]
    
    print(f"🔧 Compiling {dsl_file}...")
    compiled_rules, errors = compiler.compile_file(dsl_file)
    
    print("\n" + compiler.format_errors())
    
    if compiled_rules:
        print(f"\n✅ Successfully compiled {len(compiled_rules)} rules")
        
        if output_file:
            # Write to YAML
            with open(output_file, 'w') as f:
                yaml.dump({"rules": compiled_rules}, f, default_flow_style=False, sort_keys=False)
            print(f"📝 Written to {output_file}")
        else:
            # Print to stdout
            print("\n📋 Compiled Rules:")
            print(yaml.dump({"rules": compiled_rules}, default_flow_style=False, sort_keys=False))
    else:
        print("\n❌ Compilation failed")
        sys.exit(1)
