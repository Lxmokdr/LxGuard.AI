"""
Redis Cache Manager for Expert Agent

Provides TTL-based caching with governance-aware key generation.
All cache keys include user context to prevent role-based leaks.
"""
import redis
import json
import os
from typing import Any, Optional
from dotenv import load_dotenv

load_dotenv()

# Redis connection configuration
# Priority: REDIS_URL > Individual components
REDIS_URL = os.getenv("REDIS_URL")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

# Default TTL (1 hour)
DEFAULT_TTL = 3600


class CacheManager:
    """Redis cache manager with JSON serialization"""
    
    def __init__(self):
        if REDIS_URL:
            self.client = redis.from_url(REDIS_URL, decode_responses=True)
        else:
            self.client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB,
                password=REDIS_PASSWORD,
                decode_responses=True
            )
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key (should be generated via cache_governance)
        
        Returns:
            Cached value or None if not found
        """
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = DEFAULT_TTL) -> bool:
        """
        Set value in cache with TTL.
        
        Args:
            key: Cache key (should be generated via cache_governance)
            value: Value to cache (must be JSON-serializable)
            ttl: Time to live in seconds
        
        Returns:
            True if successful, False otherwise
        """
        try:
            serialized = json.dumps(value)
            self.client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete a specific cache entry"""
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """
        Clear all keys matching a pattern.
        
        Args:
            pattern: Redis pattern (e.g., "nlp:*")
        
        Returns:
            Number of keys deleted
        """
        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception as e:
            print(f"Cache clear pattern error: {e}")
            return 0
    
    def flush_all(self) -> bool:
        """Clear entire cache database (use with caution)"""
        try:
            self.client.flushdb()
            return True
        except Exception as e:
            print(f"Cache flush error: {e}")
            return False
    
    def ping(self) -> bool:
        """Check if Redis is accessible"""
        try:
            return self.client.ping()
        except Exception:
            return False


# Global cache instance
cache = CacheManager()


# ============================================================================
# DEPRECATED: Old cache key generators (kept for backward compatibility)
# Use cache_governance.py for new implementations
# ============================================================================

def nlp_cache_key(query: str) -> str:
    """
    DEPRECATED: Use cache_governance.nlp_cache_key() instead.
    
    This version does NOT include user context and is vulnerable to
    governance leaks.
    """
    import hashlib
    import warnings
    warnings.warn(
        "nlp_cache_key() is deprecated. Use cache_governance.nlp_cache_key() "
        "with user_id and role parameters.",
        DeprecationWarning,
        stacklevel=2
    )
    return f"nlp:{hashlib.sha256(query.encode()).hexdigest()[:16]}"


def retrieval_cache_key(query: str, intent: str, top_k: int = 5) -> str:
    """
    DEPRECATED: Use cache_governance.retrieval_cache_key() instead.
    
    This version does NOT include user context and is vulnerable to
    governance leaks.
    """
    import hashlib
    import warnings
    warnings.warn(
        "retrieval_cache_key() is deprecated. Use cache_governance.retrieval_cache_key() "
        "with user_id and role parameters.",
        DeprecationWarning,
        stacklevel=2
    )
    query_hash = hashlib.sha256(query.encode()).hexdigest()[:16]
    return f"retrieval:{query_hash}:{intent}:{top_k}"


def document_cache_key(document_id: int) -> str:
    """
    Generate cache key for document metadata.
    
    Note: This is generally safe as document content is role-agnostic,
    but consider using cache_governance.document_cache_key() if access
    levels are involved.
    """
    return f"doc:{document_id}"
