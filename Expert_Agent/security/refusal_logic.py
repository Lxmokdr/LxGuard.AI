from enum import Enum
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime

class RefusalReason(Enum):
    """
    Standardized reasons for refusing to answer a query.
    These are used by the Decision Authority to explicitely categorize
    why a request was denied, enabling auditability and drift detection.
    """
    SECURITY_PII = "SECURITY_PII"             # PII detected in query
    SECURITY_INJECTION = "SECURITY_INJECTION" # Injection attack detected
    RBAC_INSUFFICIENT = "RBAC_INSUFFICIENT"   # User lacks role/permission
    POLICY_VIOLATION = "POLICY_VIOLATION"     # Expert Rule explicitly forbids this
    ONTOLOGY_INVALID = "ONTOLOGY_INVALID"     # Intent is invalid or deprecated
    EVIDENCE_INSUFFICIENT = "EVIDENCE_INSUFFICIENT" # Not enough grounded evidence
    EVIDENCE_EXPIRED = "EVIDENCE_EXPIRED"     # Evidence exists but is too old
    UNCERTAINTY = "UNCERTAINTY"               # NLP confidence too low
    SAFETY_HALLUCINATION = "SAFETY_HALLUCINATION" # Answer validation failed
    SAFETY_FORBIDDEN_TOPIC = "SAFETY_FORBIDDEN_TOPIC" # Generated answer touched forbidden topic

@dataclass
class RefusalContext:
    """
    Structured context for a refusal decision.
    This object is serialized into the audit log.
    """
    reason: RefusalReason
    message: str
    intent: Optional[str] = None
    user_role: Optional[str] = None
    rule_id: Optional[str] = None
    evidence_gaps: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.isoformat(datetime.now()))

class ApprovedRefusal(Exception):
    """
    A 'happy path' exception indicating the system successfully 
    determined it should NOT answer. This is NOT a system error.
    """
    def __init__(self, context: RefusalContext):
        self.context = context
        super().__init__(f"Refusal: {context.reason.value} - {context.message}")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "refusal": True,
            "reason": self.context.reason.value,
            "message": self.context.message,
            "context": {
                "intent": self.context.intent,
                "rule_id": self.context.rule_id,
                "evidence_gaps": self.context.evidence_gaps,
                "timestamp": self.context.timestamp
            }
        }
