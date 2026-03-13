from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Any
from enum import Enum, auto
import uuid

# --- Authority Levels ---
class AuthorityLevel(Enum):
    """
    Hierarchical authority levels for evidence.
    Higher values override lower values.
    """
    UNVERIFIED = 0    # External web, user uploads without review
    COMMUNITY = 1     # StackOverflow, GitHub Issues
    VENDOR_DOCS = 5   # Official Next.js docs (public)
    INTERNAL_WIKI = 8 # Internal Confluence (reviewed)
    POLICY = 10       # Official Company Policy / Architecture Specs

# --- Invariants ---

@dataclass
class EvidenceObject:
    """
    A single piece of evidence with strict metadata constraints.
    Unlike a 'chunk', this carries authority and lifecycle info.
    """
    content: str
    source_doc: str
    authority: AuthorityLevel
    last_updated: datetime
    version: str = "1.0"
    tags: List[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def is_expired(self, max_age_days: int = 365) -> bool:
        """Contract: Evidence must not be older than X days."""
        age = datetime.now() - self.last_updated
        return age.days > max_age_days

    def meets_authority(self, min_level: AuthorityLevel) -> bool:
        """Contract: Evidence must meet minimum authority level."""
        return self.authority.value >= min_level.value

@dataclass
class AnswerContract:
    """
    The legal binding agreement for a generated answer.
    The system MUST guarantee these properties before releasing an answer.
    """
    intent: str
    min_authority: AuthorityLevel
    required_citations: bool
    forbidden_topics: List[str]
    max_hallucination_score: float = 0.1
    
    def validate(self, answer_text: str, cited_evidence: List[EvidenceObject]) -> List[str]:
        """
        Validates the answer against the contract.
        Returns a list of violation messages (empty if valid).
        """
        violations = []
        
        # 1. Authority Check
        for ev in cited_evidence:
            if not ev.meets_authority(self.min_authority):
                violations.append(f"Cited evidence '{ev.source_doc}' has authority {ev.authority.name} < {self.min_authority.name}")

        # 2. Citation Requirement
        if self.required_citations and not cited_evidence:
            violations.append("Answer requires citations but none provided.")

        # 3. Forbidden Topics (Basic string check for now)
        for topic in self.forbidden_topics:
            if topic.lower() in answer_text.lower():
                violations.append(f"Answer mentions forbidden topic: '{topic}'")

        return violations
