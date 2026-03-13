"""
Ontology Validator - Formal Intent Relationship Validator
Responsibilities:
- Validate intent compatibility (mutual exclusivity)
- Check prerequisite satisfaction
- Assess risk levels
- Enforce ontological constraints

This is SYMBOLIC VALIDATION of intent relationships.
"""

import json
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass
from pathlib import Path
from api.auth import User


@dataclass
class ValidationResult:
    """Result of ontology validation"""
    valid: bool
    reason: str
    conflicts: List[str]
    missing_prerequisites: List[str]
    risk_assessment: Dict[str, Any]
    recommendations: List[str]


@dataclass
class IntentMetadata:
    """Metadata for an intent from the ontology"""
    name: str
    parent: Optional[str]
    description: str
    risk_level: str
    mutually_exclusive: List[str]
    prerequisites: Dict[str, List[str]]
    compatible_with: List[str]
    priority: int
    specificity: str
    rbac_default: List[str]
    metadata: Dict[str, Any]


class OntologyValidator:
    """
    Formal Ontology Validator - Enforces semantic constraints on intents.
    Ensures that intent combinations are logically valid.
    """
    
    def __init__(self, ontology_path: Optional[str] = None, db_intents: Optional[List[Dict[str, Any]]] = None):
        """Initialize validator with formal ontology or database intents"""
        if ontology_path:
            self.ontology_path = Path(ontology_path)
        else:
            # Default to config/intent_ontology.json relative to the root Expert_Agent dir
            self.ontology_path = Path(__file__).parent.parent / "config" / "intent_ontology.json"
        
        self.ontology_data = self._load_ontology()
        self.intents: Dict[str, IntentMetadata] = self._parse_intents()
        
        # Override or supplement with DB intents if provided
        if db_intents:
            self._merge_db_intents(db_intents)
            
        self.risk_levels = self.ontology_data.get("risk_levels", {})
        self.categories = self.ontology_data.get("intent_categories", {})
        print(f"🔍 Ontology Validator initialized (Intents: {len(self.intents)})")

    def _merge_db_intents(self, db_intents: List[Dict[str, Any]]):
        """Merge database intents into the ontology structure"""
        for i_data in db_intents:
            name = i_data["name"]
            # If exists, update risk and other metadata
            if name in self.intents:
                meta = self.intents[name]
                meta.risk_level = i_data.get("risk_level", meta.risk_level)
                meta.description = i_data.get("description", meta.description)
                # Store extra fields in metadata dict
                meta.metadata["requires_approval"] = i_data.get("requires_approval", False)
                meta.metadata["audit_level"] = i_data.get("audit_level", "standard")
            else:
                # New intent from DB
                self.intents[name] = IntentMetadata(
                    name=name,
                    parent=None,
                    description=i_data.get("description", ""),
                    risk_level=i_data.get("risk_level", "low"),
                    mutually_exclusive=[],
                    prerequisites={"system_requirements": [], "intent_requirements": []},
                    compatible_with=[],
                    priority=5,
                    specificity="medium",
                    rbac_default=["admin", "employee", "guest"] if i_data.get("risk_level") == "low" else ["admin"],
                    metadata={
                        "requires_approval": i_data.get("requires_approval", False),
                        "audit_level": i_data.get("audit_level", "standard")
                    }
                )
    
    def _load_ontology(self) -> Dict[str, Any]:
        """Load ontology from JSON file"""
        try:
            with open(self.ontology_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️  Ontology file not found: {self.ontology_path}")
            return {"intents": [], "risk_levels": {}, "intent_categories": {}}
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in ontology file: {e}")
            return {"intents": [], "risk_levels": {}, "intent_categories": {}}
    
    def _parse_intents(self) -> Dict[str, IntentMetadata]:
        """Parse intents into structured metadata"""
        intents = {}
        for intent_data in self.ontology_data.get("intents", []):
            intent = IntentMetadata(
                name=intent_data["name"],
                parent=intent_data.get("parent"),
                description=intent_data.get("description", ""),
                risk_level=intent_data.get("risk_level", "low"),
                mutually_exclusive=intent_data.get("mutually_exclusive", []),
                prerequisites=intent_data.get("prerequisites", {"system_requirements": [], "intent_requirements": []}),
                compatible_with=intent_data.get("compatible_with", []),
                priority=intent_data.get("priority", 5),
                specificity=intent_data.get("specificity", "medium"),
                rbac_default=intent_data.get("rbac_default", []),
                metadata=intent_data.get("metadata", {})
            )
            intents[intent.name] = intent
        return intents
    
    def validate_intent_compatibility(self, intent_a: str, intent_b: str) -> Tuple[bool, str]:
        """
        Check if two intents can coexist.
        Returns: (compatible, reason)
        """
        if intent_a not in self.intents or intent_b not in self.intents:
            return False, f"Unknown intent: {intent_a if intent_a not in self.intents else intent_b}"
        
        intent_a_meta = self.intents[intent_a]
        intent_b_meta = self.intents[intent_b]
        
        # Check mutual exclusivity (bidirectional)
        if intent_b in intent_a_meta.mutually_exclusive:
            return False, f"{intent_a} is mutually exclusive with {intent_b}"
        
        if intent_a in intent_b_meta.mutually_exclusive:
            return False, f"{intent_b} is mutually exclusive with {intent_a}"
        
        # Check if explicitly compatible
        if intent_b in intent_a_meta.compatible_with or intent_a in intent_b_meta.compatible_with:
            return True, f"{intent_a} and {intent_b} are explicitly compatible"
        
        # Check parent-level exclusivity
        if intent_a_meta.parent and intent_b_meta.parent:
            if intent_a_meta.parent in intent_b_meta.mutually_exclusive:
                return False, f"Parent category conflict: {intent_a_meta.parent} vs {intent_b}"
        
        # Default: compatible if no explicit conflict
        return True, "No conflicts detected"
    
    def check_prerequisites(self, intent: str, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Verify prerequisite satisfaction.
        Context should contain:
        - 'satisfied_intents': List of intents already satisfied
        - 'system_capabilities': List of available system requirements
        
        Returns: (satisfied, missing_prerequisites)
        """
        if intent not in self.intents:
            return False, [f"Unknown intent: {intent}"]
        
        intent_meta = self.intents[intent]
        missing = []
        
        # Check system requirements
        system_capabilities = context.get("system_capabilities", [])
        for req in intent_meta.prerequisites.get("system_requirements", []):
            if req not in system_capabilities:
                missing.append(f"System requirement: {req}")
        
        # Check intent prerequisites
        satisfied_intents = context.get("satisfied_intents", [])
        for req_intent in intent_meta.prerequisites.get("intent_requirements", []):
            if req_intent not in satisfied_intents:
                missing.append(f"Intent prerequisite: {req_intent}")
        
        return len(missing) == 0, missing
    
    def get_risk_level(self, intent: str) -> Dict[str, Any]:
        """
        Return risk classification for an intent.
        Includes risk level, approval requirements, and audit level.
        """
        if intent not in self.intents:
            return {
                "risk_level": "unknown",
                "requires_approval": True,
                "audit_level": "comprehensive",
                "description": "Unknown intent - treated as high risk"
            }
        
        intent_meta = self.intents[intent]
        risk_level = intent_meta.risk_level
        risk_config = self.risk_levels.get(risk_level, {})
        
        # Check DB-sourced overrides in metadata
        requires_approval = intent_meta.metadata.get("requires_approval")
        if requires_approval is None:
            requires_approval = risk_config.get("requires_approval", False)
            
        audit_level = intent_meta.metadata.get("audit_level")
        if audit_level is None:
            audit_level = risk_config.get("audit_level", "standard")
            
        return {
            "risk_level": risk_level,
            "requires_approval": requires_approval,
            "audit_level": audit_level,
            "description": intent_meta.description or risk_config.get("description", "")
        }
    
    def validate_intent_for_user(self, intent: str, user: User) -> ValidationResult:
        """
        Comprehensive validation of intent for a specific user.
        Checks RBAC, prerequisites, and risk level.
        """
        if intent not in self.intents:
            return ValidationResult(
                valid=False,
                reason=f"Intent '{intent}' not found in ontology",
                conflicts=[],
                missing_prerequisites=[],
                risk_assessment={},
                recommendations=["Use 'General' intent for unclassified queries"]
            )
        
        intent_meta = self.intents[intent]
        conflicts = []
        missing_prereqs = []
        recommendations = []
        
        # Check RBAC
        if user.role.value not in intent_meta.rbac_default:
            return ValidationResult(
                valid=False,
                reason=f"User role '{user.role.value}' not authorized for intent '{intent}'",
                conflicts=[f"RBAC: Required roles: {intent_meta.rbac_default}"],
                missing_prerequisites=[],
                risk_assessment=self.get_risk_level(intent),
                recommendations=[f"Contact admin for access to {intent}"]
            )
        
        # Get risk assessment
        risk_assessment = self.get_risk_level(intent)
        
        # Check if approval is required
        if risk_assessment["requires_approval"]:
            recommendations.append(f"This intent requires approval due to {risk_assessment['risk_level']} risk level")
        
        return ValidationResult(
            valid=True,
            reason=f"Intent '{intent}' is valid for user {user.username}",
            conflicts=conflicts,
            missing_prerequisites=missing_prereqs,
            risk_assessment=risk_assessment,
            recommendations=recommendations
        )
    
    def resolve_intent_conflicts(self, intents: List[str]) -> Dict[str, Any]:
        """
        Given multiple intents, identify conflicts and suggest resolution.
        Returns the highest priority non-conflicting intent.
        """
        if not intents:
            return {
                "resolved_intent": "General",
                "reason": "No intents provided",
                "conflicts": [],
                "rejected": []
            }
        
        # Build conflict matrix
        conflicts = []
        for i, intent_a in enumerate(intents):
            for intent_b in intents[i+1:]:
                compatible, reason = self.validate_intent_compatibility(intent_a, intent_b)
                if not compatible:
                    conflicts.append({
                        "intent_a": intent_a,
                        "intent_b": intent_b,
                        "reason": reason
                    })
        
        if not conflicts:
            # No conflicts, return highest priority
            valid_intents = [i for i in intents if i in self.intents]
            if not valid_intents:
                return {
                    "resolved_intent": "General",
                    "reason": "No valid intents found",
                    "conflicts": [],
                    "rejected": intents
                }
            
            sorted_intents = sorted(valid_intents, key=lambda x: self.intents[x].priority, reverse=True)
            return {
                "resolved_intent": sorted_intents[0],
                "reason": f"Highest priority among {len(valid_intents)} compatible intents",
                "conflicts": [],
                "rejected": sorted_intents[1:]
            }
        
        # Resolve conflicts by priority and specificity
        intent_scores = {}
        for intent in intents:
            if intent not in self.intents:
                continue
            
            # Count how many conflicts this intent has
            conflict_count = sum(1 for c in conflicts if intent in [c["intent_a"], c["intent_b"]])
            
            # Score = priority - (conflict_count * penalty)
            intent_meta = self.intents[intent]
            specificity_bonus = {"high": 2, "medium": 1, "low": 0}.get(intent_meta.specificity, 0)
            score = intent_meta.priority + specificity_bonus - (conflict_count * 3)
            intent_scores[intent] = score
        
        if not intent_scores:
            return {
                "resolved_intent": "General",
                "reason": "All intents invalid",
                "conflicts": conflicts,
                "rejected": intents
            }
        
        # Select highest scoring intent
        resolved_intent = max(intent_scores, key=intent_scores.get)
        rejected = [i for i in intents if i != resolved_intent]
        
        return {
            "resolved_intent": resolved_intent,
            "reason": f"Resolved conflicts using priority and specificity (score: {intent_scores[resolved_intent]})",
            "conflicts": conflicts,
            "rejected": rejected
        }
    
    def get_intent_metadata(self, intent: str) -> Optional[IntentMetadata]:
        """Get complete metadata for an intent"""
        return self.intents.get(intent)
    
    def list_compatible_intents(self, intent: str) -> List[str]:
        """Get all intents compatible with the given intent"""
        if intent not in self.intents:
            return []
        
        intent_meta = self.intents[intent]
        compatible = []
        
        for other_intent in self.intents:
            if other_intent == intent:
                continue
            
            is_compatible, _ = self.validate_intent_compatibility(intent, other_intent)
            if is_compatible:
                compatible.append(other_intent)
        
        return compatible
    
    def get_ontology_stats(self) -> Dict[str, Any]:
        """Get statistics about the ontology"""
        return {
            "total_intents": len(self.intents),
            "categories": list(self.categories.keys()),
            "risk_levels": {
                level: sum(1 for i in self.intents.values() if i.risk_level == level)
                for level in self.risk_levels.keys()
            },
            "intents_by_category": {
                cat: sum(1 for i in self.intents.values() if i.parent == cat)
                for cat in self.categories.keys()
            }
        }


# Example usage and testing
if __name__ == "__main__":
    from api.auth import User, UserRole
    
    validator = OntologyValidator()
    
    print("\n" + "="*60)
    print("ONTOLOGY STATISTICS")
    print("="*60)
    stats = validator.get_ontology_stats()
    print(f"Total Intents: {stats['total_intents']}")
    print(f"Categories: {', '.join(stats['categories'])}")
    print(f"Risk Distribution: {stats['risk_levels']}")
    
    print("\n" + "="*60)
    print("COMPATIBILITY TESTING")
    print("="*60)
    
    # Test 1: Compatible intents
    compatible, reason = validator.validate_intent_compatibility("ProjectInitialization", "EnvironmentSetup")
    print(f"\n✓ ProjectInitialization + EnvironmentSetup: {compatible}")
    print(f"  Reason: {reason}")
    
    # Test 2: Mutually exclusive intents
    compatible, reason = validator.validate_intent_compatibility("ProjectInitialization", "Deployment")
    print(f"\n✗ ProjectInitialization + Deployment: {compatible}")
    print(f"  Reason: {reason}")
    
    print("\n" + "="*60)
    print("PREREQUISITE TESTING")
    print("="*60)
    
    # Test 3: Prerequisites satisfied
    context = {
        "system_capabilities": ["Node.js", "npm"],
        "satisfied_intents": ["ProjectInitialization"]
    }
    satisfied, missing = validator.check_prerequisites("ComponentDevelopment", context)
    print(f"\n✓ ComponentDevelopment prerequisites: {satisfied}")
    if missing:
        print(f"  Missing: {missing}")
    
    # Test 4: Prerequisites not satisfied
    context_incomplete = {
        "system_capabilities": ["Node.js"],
        "satisfied_intents": []
    }
    satisfied, missing = validator.check_prerequisites("Deployment", context_incomplete)
    print(f"\n✗ Deployment prerequisites: {satisfied}")
    print(f"  Missing: {missing}")
    
    print("\n" + "="*60)
    print("RISK ASSESSMENT")
    print("="*60)
    
    # Test 5: Risk levels
    for intent in ["ProjectInitialization", "Configuration", "Deployment", "Production"]:
        risk = validator.get_risk_level(intent)
        print(f"\n{intent}:")
        print(f"  Risk Level: {risk['risk_level']}")
        print(f"  Requires Approval: {risk['requires_approval']}")
        print(f"  Audit Level: {risk['audit_level']}")
    
    print("\n" + "="*60)
    print("RBAC VALIDATION")
    print("="*60)
    
    # Test 6: RBAC validation
    admin = User(id="1", username="Alice", role=UserRole.ADMIN)
    guest = User(id="2", username="Bob", role=UserRole.GUEST)
    
    for user in [admin, guest]:
        result = validator.validate_intent_for_user("Deployment", user)
        print(f"\n{user.username} ({user.role.value}) → Deployment:")
        print(f"  Valid: {result.valid}")
        print(f"  Reason: {result.reason}")
        if result.recommendations:
            print(f"  Recommendations: {result.recommendations}")
    
    print("\n" + "="*60)
    print("CONFLICT RESOLUTION")
    print("="*60)
    
    # Test 7: Resolve conflicts
    conflicting_intents = ["ProjectInitialization", "Deployment", "EnvironmentSetup"]
    resolution = validator.resolve_intent_conflicts(conflicting_intents)
    print(f"\nInput intents: {conflicting_intents}")
    print(f"Resolved to: {resolution['resolved_intent']}")
    print(f"Reason: {resolution['reason']}")
    print(f"Conflicts detected: {len(resolution['conflicts'])}")
    print(f"Rejected: {resolution['rejected']}")
    
    print("\n" + "="*60)
    print("COMPATIBLE INTENTS")
    print("="*60)
    
    # Test 8: List compatible intents
    compatible_list = validator.list_compatible_intents("Routing")
    print(f"\nIntents compatible with 'Routing':")
    for intent in compatible_list[:5]:
        print(f"  - {intent}")
