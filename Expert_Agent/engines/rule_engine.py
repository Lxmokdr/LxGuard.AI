# rule_engine.py

class RuleEngine:
    def __init__(self):
        self.rules = [
            {
                "id": "RULE_SETUP",
                "condition": lambda facts: any(word in facts.get("keywords", []) 
                   for word in ["setup", "create", "new", "project", "initialize"]),
                "action": lambda facts: {"topic": "setup", "exclude_docs": ["deployment.md"]},
                "priority": 10,
                "description": "If intent is creation/setup → select setup docs and exclude deployment"
            },
            {
                "id": "RULE_INSTALL",
                "condition": lambda facts: any(word in facts.get("keywords", []) 
                   for word in ["install", "installation", "npm", "yarn"]),
                "action": lambda facts: {"topic": "setup"},
                "priority": 9,
                "description": "If intent is installation → select setup docs"
            },
            {
                "id": "RULE_OPERATIONS",
                "condition": lambda facts: any(word in facts.get("keywords", []) 
                   for word in ["deploy", "deployment", "build", "production", "docker", "vercel"]),
                "action": lambda facts: {"topic": "operations"},
                "priority": 8,
                "description": "If intent is operations/deployment → select operations docs"
            },
            {
                "id": "RULE_COMPONENTS",
                "condition": lambda facts: any(word in facts.get("keywords", []) 
                    for word in ["component", "image", "link", "button", "ui", "header"]),
                "action": lambda facts: {"topic": "components"},
                "priority": 7,
                "description": "If question is about components → select components documents"
            },
            {
                "id": "RULE_ROUTING",
                "condition": lambda facts: any(word in facts.get("keywords", []) 
                    for word in ["routing", "route", "path", "page", "layout", "navigation", "pages"]),
                "action": lambda facts: {"topic": "routing"},
                "priority": 6,
                "description": "If question is about routing → select routing documents"
            },
            {
                "id": "RULE_CONFIG",
                "condition": lambda facts: any(word in facts.get("keywords", []) 
                    for word in ["config", "configuration", "settings", "options"]),
                "action": lambda facts: {"topic": "configuration"},
                "priority": 6,
                "description": "If question is about configuration → select configuration documents"
            },
            {
                "id": "RULE_CLI",
                "condition": lambda facts: any(word in facts.get("keywords", []) 
                    for word in ["command", "cli", "terminal"]),
                "action": lambda facts: {"topic": "setup"},
                "priority": 5,
                "description": "If question is about CLI commands → select setup/CLI documents"
            },
            {
                "id": "RULE_FUNCTIONS",
                "condition": lambda facts: any(word in facts.get("keywords", []) 
                    for word in ["function", "fetch", "redirect", "data", "api", "server", "async", "await", "ssr", "csr", "rendering"]),
                "action": lambda facts: {"topic": "functions"},
                "priority": 4,
                "description": "If question is about functions or rendering → select functions documents"
            }
        ]
    
    def apply_rules(self, facts):
        """Applies rules using forward chaining"""
        activated_rules = []
        new_facts = facts.copy()
        
        # Sort rules by priority (high priority first)
        sorted_rules = sorted(self.rules, key=lambda x: x["priority"], reverse=True)
        
        for rule in sorted_rules:
            if rule["condition"](new_facts):
                # Execute the rule's action
                result = rule["action"](new_facts)
                new_facts.update(result)
                activated_rules.append({
                    "id": rule["id"],
                    "description": rule["description"]
                })
        
        return new_facts, activated_rules

    def get_rules_metadata(self):
        """Returns metadata for all rules for Admin UI"""
        return [
            {
                "id": rule["id"],
                "description": rule["description"],
                "priority": rule["priority"]
            }
            for rule in self.rules
        ]
