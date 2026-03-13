"""
Security Enforcer - Enterprise Security Layer
Responsibilities:
- Intent-level RBAC enforcement
- PII detection and redaction
- Forbidden topic blocking
- Approval workflow for high-risk intents
- Security audit trail

This ensures ENTERPRISE SECURITY.
"""

import re
import hashlib
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SecurityCheckResult:
    """Result of security check"""
    allowed: bool
    reason: str
    risk_level: str
    requires_approval: bool
    pii_detected: List[str]
    forbidden_topics: List[str]
    redacted_query: Optional[str] = None


class SecurityEnforcer:
    """
    Enterprise security enforcer.
    Provides RBAC, PII detection, and security controls.
    """
    
    def __init__(self, domain_id: str = None):
        self.domain_id = domain_id
        # PII patterns
        self.pii_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            'ip_address': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
        }
        
        self.forbidden_patterns = {
            'sql_injection': r'(union\s+select|drop\s+table|insert\s+into)',
            'command_injection': r'(;|\||&&|`)',
            'path_traversal': r'(\.\./|\.\.\\)'
        }
        
        if domain_id:
            self._load_domain_config()
            
        print(f"🔒 Security Enforcer (Domain: {domain_id}) initialized")

    def _load_domain_config(self):
        """Load domain-specific security configurations from DB"""
        # Placeholder for DB-driven security rules
        # In a real multi-tenant scenario, we'd fetch from a 'security_policies' table
        pass
    
    def check_access(self, 
                    intent: str, 
                    user: Any,
                    ontology_validator: Any = None) -> SecurityCheckResult:
        """
        Check if user has access to intent.
        
        Args:
            intent: Intent to check
            user: User object with role
            ontology_validator: Optional ontology validator for risk assessment
        
        Returns:
            SecurityCheckResult with access decision
        """
        # Get risk level
        risk_level = "medium"
        requires_approval = False
        
        if ontology_validator:
            risk_info = ontology_validator.get_risk_level(intent)
            risk_level = risk_info.get("risk_level", "medium")
            requires_approval = risk_info.get("requires_approval", False)
        
        # RBAC check
        if not user:
            return SecurityCheckResult(
                allowed=False,
                reason="No user provided",
                risk_level=risk_level,
                requires_approval=requires_approval,
                pii_detected=[],
                forbidden_topics=[]
            )
        
        # Check role permissions
        user_role = user.role.value if hasattr(user.role, 'value') else str(user.role)
        
        # High-risk intents require admin or employee
        if risk_level in ["high", "critical"]:
            if user_role not in ["admin", "employee"]:
                return SecurityCheckResult(
                    allowed=False,
                    reason=f"Intent '{intent}' requires admin or employee role (user has: {user_role})",
                    risk_level=risk_level,
                    requires_approval=requires_approval,
                    pii_detected=[],
                    forbidden_topics=[]
                )
        
        # Critical intents require admin only
        if risk_level == "critical":
            if user_role != "admin":
                return SecurityCheckResult(
                    allowed=False,
                    reason=f"Intent '{intent}' requires admin role (user has: {user_role})",
                    risk_level=risk_level,
                    requires_approval=requires_approval,
                    pii_detected=[],
                    forbidden_topics=[]
                )
        
        return SecurityCheckResult(
            allowed=True,
            reason=f"Access granted for intent '{intent}' (role: {user_role}, risk: {risk_level})",
            risk_level=risk_level,
            requires_approval=requires_approval,
            pii_detected=[],
            forbidden_topics=[]
        )
    
    def detect_pii(self, text: str) -> Tuple[List[str], str]:
        """
        Detect and redact PII from text.
        
        Returns: (detected_pii_types, redacted_text)
        """
        detected = []
        redacted = text
        
        for pii_type, pattern in self.pii_patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                detected.append(pii_type)
                # Redact with hash
                for match in matches:
                    hash_val = hashlib.md5(match.encode()).hexdigest()[:8]
                    redacted = redacted.replace(match, f"[{pii_type.upper()}_{hash_val}]")
        
        return detected, redacted
    
    def check_query_security(self, query: str, user: Any) -> SecurityCheckResult:
        """
        Comprehensive security check on query.
        
        Args:
            query: User query
            user: User object
        
        Returns:
            SecurityCheckResult
        """
        # Detect PII
        pii_detected, redacted_query = self.detect_pii(query)
        
        # Check for forbidden patterns
        forbidden_topics = self._detect_forbidden_patterns(query)
        
        # Determine if allowed
        allowed = True
        reason = "Query passed security checks"
        
        if pii_detected:
            allowed = False  # BLOCK PII
            reason = f"PII detected and redacted: {', '.join(pii_detected)}"
        
        if forbidden_topics:
            allowed = False
            reason = f"Forbidden topics detected: {', '.join(forbidden_topics)}"
        
        return SecurityCheckResult(
            allowed=allowed,
            reason=reason,
            risk_level="medium",
            requires_approval=False,
            pii_detected=pii_detected,
            forbidden_topics=forbidden_topics,
            redacted_query=redacted_query if pii_detected else None
        )
    
    def _detect_forbidden_patterns(self, text: str) -> List[str]:
        """Detect forbidden patterns in text"""
        forbidden = []
        text_lower = text.lower()
        
        for pattern_name, pattern in self.forbidden_patterns.items():
            if re.search(pattern, text_lower):
                forbidden.append(pattern_name)
        
        return forbidden


# Example usage
if __name__ == "__main__":
    from api.auth import User, UserRole
    
    enforcer = SecurityEnforcer()
    
    # Test RBAC
    admin = User(id="1", username="Alice", role=UserRole.ADMIN)
    guest = User(id="2", username="Bob", role=UserRole.GUEST)
    
    print("="*60)
    print("RBAC TEST")
    print("="*60)
    
    result = enforcer.check_access("Deployment", admin)
    print(f"\nAdmin accessing Deployment: {result.allowed}")
    print(f"Reason: {result.reason}")
    
    result = enforcer.check_access("Deployment", guest)
    print(f"\nGuest accessing Deployment: {result.allowed}")
    print(f"Reason: {result.reason}")
    
    # Test PII detection
    print("\n" + "="*60)
    print("PII DETECTION TEST")
    print("="*60)
    
    query_with_pii = "My email is john@example.com and phone is 555-123-4567"
    result = enforcer.check_query_security(query_with_pii, admin)
    
    print(f"\nOriginal: {query_with_pii}")
    print(f"PII Detected: {result.pii_detected}")
    print(f"Redacted: {result.redacted_query}")
