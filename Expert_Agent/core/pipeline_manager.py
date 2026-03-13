
import threading
from typing import Dict, Tuple, Optional
from core.hybrid_pipeline import HybridPipeline

class PipelineManager:
    """
    Manages and caches HybridPipeline instances for multiple domains and tenants.
    Ensures that components are properly isolated and initialized within their respective domains.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(PipelineManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        self.pipelines: Dict[Tuple[str, str], HybridPipeline] = {}
        self.lock = threading.Lock()
        
        # Shared resources (optional, can be passed to pipelines)
        self.shared_embedder = None
        
        self._initialized = True
        print("🏢 Pipeline Manager initialized")

    def get_pipeline(self, domain_id: str, tenant_id: str = None) -> HybridPipeline:
        """
        Get or create a pipeline for a specific domain and tenant.
        """
        if not domain_id:
            raise ValueError("domain_id is required to get a pipeline")
            
        key = (tenant_id, domain_id)
        
        with self.lock:
            if key not in self.pipelines:
                print(f"🏗️  Creating new pipeline for Domain: {domain_id}, Tenant: {tenant_id}")
                # Initialize new pipeline
                # In a real system, we might pass shared resources like the embedder
                self.pipelines[key] = HybridPipeline(
                    domain_id=domain_id,
                    tenant_id=tenant_id,
                    use_embeddings=True,
                    use_local_llm=True
                )
            
            return self.pipelines[key]

    def clear_cache(self, domain_id: str = None, tenant_id: str = None):
        """Clear specific or all pipelines from cache"""
        with self.lock:
            if domain_id:
                key = (tenant_id, domain_id)
                if key in self.pipelines:
                    del self.pipelines[key]
                    print(f"🧹 Cleared pipeline for Domain: {domain_id}")
            else:
                self.pipelines.clear()
                print("🧹 Cleared all pipelines")

# Global instance
pipeline_manager = PipelineManager()
