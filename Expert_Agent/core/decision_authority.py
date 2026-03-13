from typing import List, Optional, Tuple, Any, Dict
import logging
from security.refusal_logic import RefusalReason, ApprovedRefusal, RefusalContext
from data.knowledge_contracts import AnswerContract, EvidenceObject, AuthorityLevel

# Mocking dependent classes for now - these would be the actual modules
class User:
    def __init__(self, role: str):
        self.role = role

class Rule:
    def __init__(self, priority: int, intent: str, allowed: bool):
        self.priority = priority
        self.intent = intent
        self.allowed = allowed

class DecisionAuthority:
    """
    The Supreme Court of the Hybrid Agent.
    Enforces the Decision Priority Hierarchy:
    1. Security Policy (PII, Blocklist) -> HIGHEST
    2. RBAC (User Role)
    3. Expert Rules (DSL)
    4. Ontology Constraints
    5. NLP Confidence -> LOWEST
    """
    def __init__(self):
        self.logger = logging.getLogger("DecisionAuthority")
        # Hardcoded security policies for v2 prototype
        self.blocked_ips = ["1.2.3.4"]
        self.regex_pii = [r"\d{3}-\d{2}-\d{4}"] # SSN-like

    def arbitrate(self, 
                 nlp_intent: str, 
                 nlp_confidence: float, 
                 user: User, 
                 active_rules: List[Rule]) -> Tuple[str, str]:
        """
        Determines the FINAL intent or raises an ApprovedRefusal.
        Returns: (final_intent, decision_justification)
        """
        
        # 1. Security Check (Pre-Computation)
        # Note: IP/PII checks happen at Layer 0, but Authority validates the result context here if needed.
        
        # 2. RBAC Assessment
        if not self._check_rbac(nlp_intent, user.role):
            raise ApprovedRefusal(RefusalContext(
                reason=RefusalReason.RBAC_INSUFFICIENT,
                message=f"User role '{user.role}' is not authorized for intent '{nlp_intent}'.",
                intent=nlp_intent,
                user_role=user.role
            ))

        # 3. Rule Engine Override
        # Rules can explicitly BLOCK an intent even if RBAC allows it
        blocking_rule = self._find_blocking_rule(nlp_intent, active_rules)
        if blocking_rule:
             raise ApprovedRefusal(RefusalContext(
                reason=RefusalReason.POLICY_VIOLATION,
                message=f"Expert Rule explicitly blocks intent '{nlp_intent}'.",
                intent=nlp_intent,
                rule_id="RULE_BLOCK_X" # simplified
            ))
            
        # 4. Ontology Validation
        if not self._validate_ontology(nlp_intent):
             raise ApprovedRefusal(RefusalContext(
                reason=RefusalReason.ONTOLOGY_INVALID,
                message=f"Intent '{nlp_intent}' is deprecated or invalid in current ontology.",
                intent=nlp_intent
            ))

        # 5. NLP Confidence Threshold (Lowest Priority)
        # Only check confidence if no higher authority intercepted
        MIN_CONFIDENCE = 0.7
        if nlp_confidence < MIN_CONFIDENCE:
             raise ApprovedRefusal(RefusalContext(
                reason=RefusalReason.UNCERTAINTY,
                message=f"NLP Confidence {nlp_confidence} < Threshold {MIN_CONFIDENCE}",
                intent=nlp_intent
            ))

        return nlp_intent, "Authorized by Decision Authority (passed RBAC, Rules, Ontology, and NLP checks)"

    def validate_answer(self, 
                       answer_text: str, 
                       contract: AnswerContract, 
                       evidence: List[EvidenceObject]) -> bool:
        """
        Final Post-Generation Check (Layer 8 Check).
        Raises ApprovedRefusal if contract violated.
        """
        violations = contract.validate(answer_text, evidence)
        
        if violations:
             raise ApprovedRefusal(RefusalContext(
                reason=RefusalReason.SAFETY_HALLUCINATION,
                message=f"Answer violated strict contract: {'; '.join(violations)}",
                intent=contract.intent
            ))
            
        return True

    # --- Internal Logic ---

    def _check_rbac(self, intent: str, role: str) -> bool:
        # Simplified RBAC matrix for prototype
        # In real system, this queries the Auth module or DB
        restricted_intents = {"Deployment", "SecurityConfig", "UserManagement"}
        if intent in restricted_intents and role != "admin":
            return False
        return True

    def _find_blocking_rule(self, intent: str, rules: List[Rule]) -> Optional[Rule]:
        # Find highest priority rule that denies this intent
        for rule in sorted(rules, key=lambda r: r.priority, reverse=True):
            if rule.intent == intent and not rule.allowed:
                return rule
        return None

    def _validate_ontology(self, intent: str) -> bool:
        # Placeholder for OntologyValidator call
        valid_intents = {"Deployment", "General", "Help", "ProjectInitialization"}
        return intent in valid_intents
