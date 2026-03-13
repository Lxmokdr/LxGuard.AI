"""
Cache Governance - Role-Aware Cache Key Generation

Prevents governance leaks by including user context, role, and system state
in all cache keys. Ensures admin retrieval results don't leak to guest users.
"""
import hashlib
import json
from typing import Optional
from datetime import datetime


class CacheGovernance:
    """Centralized governance versioning for cache keys"""
    
    def __init__(self):
        self._rule_version_cache: Optional[str] = None
        self._settings_version_cache: Optional[str] = None
        self._last_update: Optional[datetime] = None
    
    def get_rule_version_hash(self) -> str:
        """
        Get hash of current active rules.
        
        This should be recomputed when rules are updated.
        Cache invalidation happens automatically when this changes.
        """
        # TODO: Implement actual rule versioning from database
        # For now, use a placeholder that should be replaced
        from utils.rule_manager import RuleManager
        
        try:
            rules = RuleManager().get_active_rules()
            rule_data = json.dumps(rules, sort_keys=True)
            return hashlib.sha256(rule_data.encode()).hexdigest()[:16]
        except Exception:
            # Fallback: use timestamp-based version
            return hashlib.sha256(str(datetime.utcnow().date()).encode()).hexdigest()[:16]
    
    def get_settings_version_hash(self) -> str:
        """
        Get hash of current system settings.
        
        This should be recomputed when system_settings table is updated.
        """
        # TODO: Implement actual settings versioning from database
        # For now, use a placeholder
        try:
            from api.models import SystemSetting
            from data.database import SessionLocal
            
            db = SessionLocal()
            settings = db.query(SystemSetting).all()
            settings_data = json.dumps(
                {s.key: s.value for s in settings},
                sort_keys=True
            )
            db.close()
            return hashlib.sha256(settings_data.encode()).hexdigest()[:16]
        except Exception:
            # Fallback: use date-based version
            return hashlib.sha256(str(datetime.utcnow().date()).encode()).hexdigest()[:16]
    
    def get_user_cache_context(
        self,
        user_id: str,
        role: str,
        rule_version: Optional[str] = None,
        settings_version: Optional[str] = None
    ) -> str:
        """
        Build unified cache context string.
        
        Args:
            user_id: User identifier
            role: User role (admin, employee, developer, guest)
            rule_version: Optional rule version hash (auto-fetched if None)
            settings_version: Optional settings version hash (auto-fetched if None)
        
        Returns:
            Context string for cache key: "user_id:role:rule_ver:settings_ver"
        """
        if rule_version is None:
            rule_version = self.get_rule_version_hash()
        if settings_version is None:
            settings_version = self.get_settings_version_hash()
        
        return f"{user_id}:{role}:{rule_version}:{settings_version}"
    
    def invalidate_on_rule_change(self):
        """Force cache invalidation by clearing version cache"""
        self._rule_version_cache = None
        self._last_update = datetime.utcnow()
    
    def invalidate_on_settings_change(self):
        """Force cache invalidation by clearing version cache"""
        self._settings_version_cache = None
        self._last_update = datetime.utcnow()


# Global instance
_governance = CacheGovernance()


def get_governance() -> CacheGovernance:
    """Get global governance instance"""
    return _governance


# ============================================================================
# Role-Aware Cache Key Generators
# ============================================================================

def nlp_cache_key(
    query: str,
    user_id: str,
    role: str,
    rule_version: Optional[str] = None,
    settings_version: Optional[str] = None
) -> str:
    """
    Generate governance-aware cache key for NLP analysis.
    
    SECURITY: Includes user context to prevent role-based leaks.
    
    Args:
        query: User query text
        user_id: User identifier
        role: User role (admin, employee, developer, guest)
        rule_version: Optional rule version hash
        settings_version: Optional settings version hash
    
    Returns:
        Cache key: "nlp:{query_hash}:{context_hash}"
    """
    gov = get_governance()
    context = gov.get_user_cache_context(user_id, role, rule_version, settings_version)
    
    query_hash = hashlib.sha256(query.encode()).hexdigest()[:16]
    context_hash = hashlib.sha256(context.encode()).hexdigest()[:16]
    
    return f"nlp:{query_hash}:{context_hash}"


def retrieval_cache_key(
    query: str,
    intent: str,
    user_id: str,
    role: str,
    top_k: int = 5,
    rule_version: Optional[str] = None,
    settings_version: Optional[str] = None
) -> str:
    """
    Generate governance-aware cache key for retrieval results.
    
    SECURITY: Critical for RBAC - admin retrieval must not leak to guests.
    
    Args:
        query: User query text
        intent: Final intent after arbitration
        user_id: User identifier
        role: User role (determines document access)
        top_k: Number of results
        rule_version: Optional rule version hash
        settings_version: Optional settings version hash
    
    Returns:
        Cache key: "retrieval:{query_hash}:{intent}:{top_k}:{context_hash}"
    """
    gov = get_governance()
    context = gov.get_user_cache_context(user_id, role, rule_version, settings_version)
    
    query_hash = hashlib.sha256(query.encode()).hexdigest()[:16]
    context_hash = hashlib.sha256(context.encode()).hexdigest()[:16]
    
    return f"retrieval:{query_hash}:{intent}:{top_k}:{context_hash}"


def document_cache_key(
    document_id: int,
    access_level: Optional[str] = None
) -> str:
    """
    Generate cache key for document metadata.
    
    Note: Document content is generally role-agnostic, but metadata
    might include access_level restrictions.
    
    Args:
        document_id: Document identifier
        access_level: Optional access level (internal, public, restricted)
    
    Returns:
        Cache key: "doc:{document_id}:{access_level}"
    """
    if access_level:
        return f"doc:{document_id}:{access_level}"
    return f"doc:{document_id}"


def answer_plan_cache_key(
    query: str,
    intent: str,
    user_id: str,
    role: str,
    rule_version: Optional[str] = None,
    settings_version: Optional[str] = None
) -> str:
    """
    Generate governance-aware cache key for answer plans.
    
    SECURITY: Plans may differ based on role (e.g., disclaimers for guests).
    
    Args:
        query: User query text
        intent: Final intent
        user_id: User identifier
        role: User role
        rule_version: Optional rule version hash
        settings_version: Optional settings version hash
    
    Returns:
        Cache key: "plan:{query_hash}:{intent}:{context_hash}"
    """
    gov = get_governance()
    context = gov.get_user_cache_context(user_id, role, rule_version, settings_version)
    
    query_hash = hashlib.sha256(query.encode()).hexdigest()[:16]
    context_hash = hashlib.sha256(context.encode()).hexdigest()[:16]
    
    return f"plan:{query_hash}:{intent}:{context_hash}"


# ============================================================================
# Cache Invalidation Helpers
# ============================================================================

def invalidate_user_cache(cache_client, user_id: str):
    """Invalidate all cache entries for a specific user"""
    pattern = f"*:{user_id}:*"
    keys = cache_client.keys(pattern)
    if keys:
        cache_client.delete(*keys)


def invalidate_role_cache(cache_client, role: str):
    """Invalidate all cache entries for a specific role"""
    pattern = f"*:{role}:*"
    keys = cache_client.keys(pattern)
    if keys:
        cache_client.delete(*keys)


def invalidate_on_rule_update(cache_client):
    """
    Invalidate all governance-sensitive cache on rule update.
    
    This is called when rules are modified via the admin interface.
    """
    _governance.invalidate_on_rule_change()
    # Clear all NLP, retrieval, and plan caches
    for prefix in ["nlp:", "retrieval:", "plan:"]:
        keys = cache_client.keys(f"{prefix}*")
        if keys:
            cache_client.delete(*keys)


def invalidate_on_settings_update(cache_client):
    """
    Invalidate all governance-sensitive cache on settings update.
    
    This is called when system_settings are modified.
    """
    _governance.invalidate_on_settings_change()
    # Clear all caches that depend on settings
    for prefix in ["nlp:", "retrieval:", "plan:"]:
        keys = cache_client.keys(f"{prefix}*")
        if keys:
            cache_client.delete(*keys)
