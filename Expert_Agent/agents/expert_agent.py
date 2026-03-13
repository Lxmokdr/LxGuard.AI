"""
LxGuard.AI Core - Layer 2 of Neuro-Symbolic Architecture
Responsibilities:
- Ontology (concepts + relations)
- Production rules (IF-THEN with constraints)
- Intent validation and control
- Rule enforcement
- Safety constraints

This is the BRAIN - deterministic, in charge, and authoritative.
"""

import os
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from utils.rule_loader import RuleLoader
from api.auth import AuthManager, User, UserRole
from security.ontology_validator import OntologyValidator


@dataclass
class Concept:
    """Represents a concept in the ontology"""
    name: str
    parent: Optional[str]
    requires: List[str]
    excludes: List[str]
    priority: int
    specificity: str


@dataclass
class ProductionRule:
    """IF-THEN production rule with constraints"""
    id: str
    condition: Any  # Can be a callable or list of triggers
    action: Any     # Can be a callable or dict
    priority: int
    description: str
    excludes: List[str]  # Topics to exclude when this rule fires
    required_roles: List[str] = None # Roles required to trigger this rule
    active: bool = True  # Added toggle support
    test_query: Optional[str] = None # Query to test this rule
    trigger_keywords: List[str] = None # Keywords for easy flagging

    def check_condition(self, intent: str, user: Optional[User] = None, nlp_analysis: Optional[Any] = None) -> bool:
        """Check if rule applies to intent AND user AND optionally keywords in query"""
        if not self.active:
            return False
            
        # 0. Check Trigger Keywords (Shortcut/Flagging)
        # If any trigger keyword matches the query OR nlp keywords, the rule fires
        if self.trigger_keywords and nlp_analysis:
            query_lower = nlp_analysis.query.lower()
            nlp_keywords = {k.lower() for k in nlp_analysis.keywords}
            
            for tk in self.trigger_keywords:
                tk_lower = tk.lower()
                # Direct substring match in query
                if tk_lower in query_lower:
                    return True
                # Match in lemmatized/extracted keywords (related expressions)
                if tk_lower in nlp_keywords:
                    return True
        
        # 1. Check Intent Match
        intent_match = False
        if isinstance(self.condition, list):
            intent_match = intent in self.condition
        elif callable(self.condition):
            intent_match = self.condition(intent)
            
        if not intent_match:
            return False
            
        # 2. Check Role Access (if defined)
        if self.required_roles and user:
            # Check if user role is in the required list
            # If the list contains 'admin', 'employee', then user MUST be one of those.
            if not AuthManager.check_access(user, self.required_roles):
                print(f"⛔ Rule {self.id} blocked for user {user.username} ({user.role})")
                return False
                
        return True

    def get_action(self) -> Dict[str, Any]:
        """Get the action result"""
        # Handle dict (from YAML)
        if isinstance(self.action, dict):
            return self.action
        # Handle callable (legacy or custom)
        elif callable(self.action):
            return self.action()
        return {}


class ExpertAgent:
    """
    LxGuard.AI - The deterministic brain of the system.
    Controls what must be answered and how.
    No LLM is allowed to violate these rules.
    """
    
    def __init__(self, domain_id: str = None):
        print(f"🧠 Initializing LxGuard.AI Core (Domain: {domain_id or 'Global'})...")
        self.domain_id = domain_id
        self.loader = RuleLoader(domain_id=domain_id)
        
        # Load intents from DB
        db_intents = self.loader.load_intents()
        
        self.ontology = self._load_ontology()
        self.rules = self._load_production_rules()
        self.answer_templates = self.loader.load_templates()
        
        # Initialize formal ontology validator with DB intents
        try:
            self.ontology_validator = OntologyValidator(db_intents=db_intents)
            print(f"✅ Formal Ontology Validator integrated with {len(db_intents)} DB intents")
        except Exception as e:
            import traceback
            print(f"⚠️  Ontology Validator initialization failed: {e}")
            traceback.print_exc()
            self.ontology_validator = None
        
        # Load induced Knowledge Graph (RDF/Triple based)
        from rdflib import Graph
        self.kb_graph = Graph()
        induced_path = "knowledge_base/ontology.ttl"
        if os.path.exists(induced_path):
            try:
                self.kb_graph.parse(induced_path, format="turtle")
                print(f"✅ Induced Knowledge Graph loaded from {induced_path} ({len(self.kb_graph)} triples)")
            except Exception as e:
                print(f"⚠️  Failed to load induced KG: {e}")
        
        print("✅ LxGuard.AI ready with ontology, rules, and induced KG")
        self.check_rule_conflicts()

    def check_rule_conflicts(self) -> List[Dict[str, Any]]:
        """
        Formal rule conflict detection at compile time.
        Detects rules with overlapping triggers but conflicting actions.
        """
        print("🛡️  Running formal rule conflict detection...")
        conflicts = []
        
        # Group rules by trigger
        intent_to_rules = {}
        for rule in self.rules:
            triggers = rule.condition if isinstance(rule.condition, list) else [rule.condition]
            for t in triggers:
                if t not in intent_to_rules:
                    intent_to_rules[t] = []
                intent_to_rules[t].append(rule)
        
        # Check for conflicts within each intent
        for intent, rules in intent_to_rules.items():
            if len(rules) <= 1:
                continue
                
            # Sort by priority - same priority rules for same intent is a conflict
            priority_map = {}
            for r in rules:
                if r.priority not in priority_map:
                    priority_map[r.priority] = []
                priority_map[r.priority].append(r)
            
            for priority, conflicting_rules in priority_map.items():
                if len(conflicting_rules) > 1:
                    conflict = {
                        "type": "ambiguity",
                        "intent": intent,
                        "priority": priority,
                        "rules": [r.id for r in conflicting_rules],
                        "description": f"Multiple rules with priority {priority} for intent '{intent}'"
                    }
                    conflicts.append(conflict)
                    print(f"⚠️  Rule Conflict: {conflict['description']}")

            # Check for conflicting document actions (required vs forbidden)
            required_docs = set()
            forbidden_docs = set()
            for r in rules:
                action = r.get_action()
                required_docs.update(action.get("required_docs", []))
                forbidden_docs.update(action.get("forbidden_docs", []))
            
            intersection = required_docs & forbidden_docs
            if intersection:
                conflict = {
                    "type": "logical_contradiction",
                    "intent": intent,
                    "docs": list(intersection),
                    "description": f"Contradictory document rules for '{intent}': {intersection} are both required and forbidden"
                }
                conflicts.append(conflict)
                print(f"❌ Logical Contradiction: {conflict['description']}")

        return conflicts
    
    def _load_ontology(self) -> Dict[str, Concept]:
        """Load ontology from external config"""
        raw_concepts = self.loader.load_ontology()
        concepts = {}
        
        for c in raw_concepts:
            concepts[c["name"]] = Concept(
                name=c["name"],
                parent=c.get("parent"),
                requires=c.get("requires", []),
                excludes=c.get("excludes", []),
                priority=c.get("priority", 5),
                specificity=c.get("specificity", "medium")
            )
        return concepts
    
    def _load_production_rules(self) -> List[ProductionRule]:
        """Load rules from external config"""
        raw_rules = self.loader.load_rules()
        rules = []
        
        for r in raw_rules:
            rules.append(ProductionRule(
                id=r.get("name"), # Use 'name' from DB as rule ID in logic
                condition=r.get("condition", []), # triggers list
                action=r.get("action", {}),
                priority=r.get("priority", 5),
                description=r.get("description", ""),
                excludes=r.get("excludes", []),
                required_roles=r.get("required_roles", []), # Load role constraints
                test_query=r.get("test_query"),
                trigger_keywords=r.get("trigger_keywords", [])
            ))
            
        return rules

    def log_rule_execution(self, rule_id: str, query_id: str, fired: bool, outcome: str):
        """
        Log rule execution to the database (Enterprise feature).
        """
        # Note: In a real enterprise setup, this would use the SQL engine.
        # For now, it's a structural hook.
        print(f"📝 [Audit] Rule {rule_id} {'fired' if fired else 'checked'} for query {query_id}. Outcome: {outcome}")
    
    def validate_intent(self, intent: str, nlp_analysis: Any, user: Optional[User] = None) -> Dict[str, Any]:
        """
        Validate an intent against ontology rules.
        This is where the expert agent exercises control.
        Enhanced with formal ontology validation.
        """
        if intent not in self.ontology:
            return {
                "valid": False,
                "reason": f"Intent '{intent}' not in ontology",
                "fallback": "General"
            }
        
        concept = self.ontology[intent]
        
        # Enhanced validation with formal ontology validator
        validation_result = {
            "valid": True,
            "concept": concept,
            "excludes": concept.excludes,
            "requires": concept.requires
        }
        
        # Add formal ontology validation if available
        if self.ontology_validator and user:
            formal_validation = self.ontology_validator.validate_intent_for_user(intent, user)
            validation_result["formal_validation"] = {
                "valid": formal_validation.valid,
                "reason": formal_validation.reason,
                "risk_assessment": formal_validation.risk_assessment,
                "conflicts": formal_validation.conflicts,
                "recommendations": formal_validation.recommendations
            }
            
            # Override validity if formal validation fails
            if not formal_validation.valid:
                validation_result["valid"] = False
                validation_result["reason"] = formal_validation.reason
        
        return validation_result
    
    def get_applicable_rules(self, intent: str, user: Optional[User] = None, nlp_analysis: Optional[Any] = None) -> List[ProductionRule]:
        """Get all rules applicable to an intent AND user AND query keywords"""
        applicable = []
        for rule in self.rules:
            if rule.check_condition(intent, user, nlp_analysis):
                applicable.append(rule)
        
        # Sort by priority
        applicable.sort(key=lambda r: r.priority, reverse=True)
        return applicable
    
    def get_exclusions(self, intent: str, user: Optional[User] = None) -> List[str]:
        """Get all topics excluded for this intent"""
        if intent not in self.ontology:
            return []
        
        exclusions = set(self.ontology[intent].excludes)
        
        # Add exclusions from applicable rules
        for rule in self.get_applicable_rules(intent, user):
            exclusions.update(rule.excludes)
        
        return list(exclusions)
    
    def get_answer_template(self, intent: str) -> Dict[str, Any]:
        """Get the answer template for an intent (Domain-aware)"""
        tpl = self.answer_templates.get(intent, self.answer_templates.get("General", {}))
        
        # Ensure a 'steps' list exists for the planner
        if "steps" not in tpl:
            tpl["steps"] = ["Analyze the core question.", "Provide an expert answer based on documentation.", "Check for security and compliance."]
            
        # Handle the new template structure (string template vs YAML dict)
        if isinstance(tpl, dict) and "template" in tpl:
            return {"structure": "flexible", "template": tpl["template"], "steps": tpl["steps"]}
            
        return tpl
    
    def get_eligible_documents(self, intent: str, user: Optional[User] = None) -> Dict[str, List[str]]:
        """
        Get eligible documents for an intent.
        Returns required and forbidden documents.
        """
        rules = self.get_applicable_rules(intent, user)
        
        if not rules:
            # If no rules apply (e.g. all blocked by RBAC), return restrictive default
            # Or if it's a general query with no rules
            if intent == "General":
                 return {"required": [], "forbidden": [], "topic": None}

            return {
                "required": [],
                "forbidden": [],
                "topic": None # Changed from "restricted" to None to allow semantic search fallback for unmapped intents
            }
        
        # Use the highest priority rule
        top_rule = rules[0]
        action_result = top_rule.get_action()
        
        return {
            "required": action_result.get("required_docs", []),
            "forbidden": action_result.get("forbidden_docs", []),
            "topic": action_result.get("topic", "general")
        }
    
    def is_valid_intent(self, hypothesis: Dict[str, Any], nlp_analysis: Any, user: Optional[User] = None) -> bool:
        """
        Check if an intent hypothesis is valid according to expert rules.
        This is symbolic control over probabilistic NLP.
        Enhanced with formal ontology validation.
        """
        intent = hypothesis["intent"]
        validation = self.validate_intent(intent, nlp_analysis, user)
        
        return validation["valid"]
    
    def check_intent_compatibility(self, intent_a: str, intent_b: str) -> Dict[str, Any]:
        """
        Check if two intents are compatible (not mutually exclusive).
        Uses formal ontology validator.
        """
        if not self.ontology_validator:
            return {"compatible": True, "reason": "Ontology validator not available"}
        
        compatible, reason = self.ontology_validator.validate_intent_compatibility(intent_a, intent_b)
        return {"compatible": compatible, "reason": reason}
    
    def get_risk_assessment(self, intent: str) -> Dict[str, Any]:
        """
        Get risk assessment for an intent.
        Uses formal ontology validator.
        """
        if not self.ontology_validator:
            return {"risk_level": "unknown", "requires_approval": False}
        
        return self.ontology_validator.get_risk_level(intent)
    
    def resolve_intent_conflicts(self, intents: List[str]) -> Dict[str, Any]:
        """
        Resolve conflicts between multiple intents.
        Uses formal ontology validator.
        """
        if not self.ontology_validator:
            # Fallback to priority-based resolution
            valid_intents = [i for i in intents if i in self.ontology]
            if not valid_intents:
                return {"resolved_intent": "General", "reason": "No valid intents"}
            
            sorted_intents = sorted(valid_intents, key=lambda x: self.ontology[x].priority, reverse=True)
            return {"resolved_intent": sorted_intents[0], "reason": "Highest priority"}
        
        return self.ontology_validator.resolve_intent_conflicts(intents)

    def query_knowledge_graph(self, keywords: List[str]) -> List[Dict[str, str]]:
        """
        Search the induced KG for relevant triples based on keywords.
        Returns a list of S-P-O facts.
        """
        if not self.kb_graph or len(self.kb_graph) == 0:
            return []
            
        from rdflib import RDFS, Namespace
        EX = Namespace("http://expert-agent.ai/ontology/")
        
        results = []
        seen = set()
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            # Simple keyword search on labels/URIs
            for s, p, o in self.kb_graph:
                # Get labels or local names
                s_label = str(self.kb_graph.value(s, RDFS.label) or s.split('/')[-1]).lower()
                p_label = str(p.split('/')[-1] if '#' not in p else p.split('#')[-1]).lower()
                o_label = str(self.kb_graph.value(o, RDFS.label) or o.split('/')[-1]).lower()
                
                if keyword_lower in s_label or keyword_lower in o_label:
                    fact = {
                        "subject": str(self.kb_graph.value(s, RDFS.label) or s.split('/')[-1]),
                        "predicate": p_label,
                        "object": str(self.kb_graph.value(o, RDFS.label) or o.split('/')[-1])
                    }
                    fact_key = f"{fact['subject']}-{fact['predicate']}-{fact['object']}"
                    if fact_key not in seen:
                        results.append(fact)
                        seen.add(fact_key)
                        
    def get_all_triples(self) -> List[Dict[str, Any]]:
        """
        Export all triples from the induced KG for visualization.
        """
        if not self.kb_graph:
            return []
            
        from rdflib import RDFS, Namespace, Literal
        EX = Namespace("http://expert-agent.ai/ontology/")
        results = []
        
        # Build a set of verified triple hashes for quick lookup
        verified_hashes = set()
        for s, p, o in self.kb_graph:
            if p == EX.verified_hash:
                verified_hashes.add(str(o))

        for s, p, o in self.kb_graph:
            # Skip metadata triples
            if p in [EX.verified, EX.derivedFrom, EX.verified_hash]:
                continue

            s_label = str(self.kb_graph.value(s, RDFS.label) or s.split('/')[-1])
            p_label = str(p.split('/')[-1] if '#' not in p else p.split('#')[-1])
            o_label = str(self.kb_graph.value(o, RDFS.label) or o.split('/')[-1])
            
            # Generate a hash for the triple to check verification
            import hashlib
            fact_hash = hashlib.md5(f"{str(s)}|{str(p)}|{str(o)}".encode()).hexdigest()
            
            results.append({
                "subject": s_label,
                "predicate": p_label,
                "object": o_label,
                "subject_uri": str(s),
                "predicate_uri": str(p),
                "object_uri": str(o),
                "verified": fact_hash in verified_hashes
            })
        return results

    def manage_triple(self, subject: str, predicate: str, obj: str, action: str, 
                      subject_uri: str = None, predicate_uri: str = None, object_uri: str = None) -> bool:
        """
        Manage induced triples: 'approve' (verify) or 'reject' (delete).
        """
        if not self.kb_graph:
            return False
            
        from rdflib import URIRef, Namespace, Literal
        EX = Namespace("http://expert-agent.ai/ontology/")
        
        # Normalize labels to find existing URIs if explicit URIs aren't provided
        def get_uri(label):
            import re
            slug = re.sub(r'\W+', '_', label.strip()).strip('_')
            return EX[slug]

        s_uri = URIRef(subject_uri) if subject_uri else get_uri(subject)
        p_uri = URIRef(predicate_uri) if predicate_uri else get_uri(predicate)
        o_uri = URIRef(object_uri) if object_uri else get_uri(obj)
        
        induced_path = "knowledge_base/ontology.ttl"
        
        if action == "reject":
            # Remove the specific triple
            self.kb_graph.remove((s_uri, p_uri, o_uri))
            # Also remove its verification hash if it exists
            import hashlib
            fact_hash = hashlib.md5(f"{str(s_uri)}|{str(p_uri)}|{str(o_uri)}".encode()).hexdigest()
            self.kb_graph.remove((None, EX.verified_hash, Literal(fact_hash)))
            
            try:
                self.kb_graph.serialize(destination=induced_path, format="turtle")
                print(f"🗑️ Rejected and deleted triple: {subject} {predicate} {obj}")
                return True
            except Exception as e:
                print(f"❌ Failed to save rejected triple: {e}")
                return False
                
        elif action == "approve":
            # Mark the SPECIFIC triple as verified using a hash
            import hashlib
            fact_hash = hashlib.md5(f"{str(s_uri)}|{str(p_uri)}|{str(o_uri)}".encode()).hexdigest()
            self.kb_graph.add((s_uri, EX.verified_hash, Literal(fact_hash)))
            
            try:
                self.kb_graph.serialize(destination=induced_path, format="turtle")
                print(f"✅ Approved and verified triple: {subject} {predicate} {obj}")
                return True
            except Exception as e:
                print(f"❌ Failed to save approved triple: {e}")
                return False
            
        return False


# Example usage
if __name__ == "__main__":
    agent = ExpertAgent()
    
    # Mock Users
    admin = User(id="1", username="Admin", role=UserRole.ADMIN)
    guest = User(id="2", username="Guest", role=UserRole.GUEST)

    print("\n--- Testing RBAC for Deployment ---")
    intent = "Deployment"
    
    print(f"User: {admin.username} ({admin.role})")
    docs = agent.get_eligible_documents(intent, user=admin)
    print(f"Docs: {docs}")
    
    print(f"\nUser: {guest.username} ({guest.role})")
    docs = agent.get_eligible_documents(intent, user=guest)
    print(f"Docs: {docs} (Should be restricted/empty if rule blocked)")

