
from typing import Dict, List, Any, Optional
from utils.auto_discovery import AutoDiscovery
from data.database import SessionLocal
from api.models import Document, Domain

class KnowledgeBase:
    """
    Database-driven Knowledge Base that manages:
    1. Document metadata from the 'documents' table.
    2. Syncing local files with database entries.
    """
    
    def __init__(self, domain_id: str = None, enable_auto_discovery=True):
        self.domain_id = domain_id
        
        # Combined view (metadata from DB)
        self.documents = {}
        
        # Auto-discovery
        self.auto_discovery = None
        if enable_auto_discovery:
            self.auto_discovery = AutoDiscovery()
            if domain_id:
                self.sync_with_db()
        
        if domain_id:
            self._load_from_db()
        
        print(f"📚 Knowledge Base initialized (Domain: {domain_id or 'Global'}): {len(self.documents)} documents")

    def _load_from_db(self):
        """Load document metadata from database for the active domain"""
        if not self.domain_id:
            return
            
        db = SessionLocal()
        try:
            docs = db.query(Document).filter_by(domain_id=self.domain_id).all()
            self.documents = {
                d.source: {
                    "name": d.title,
                    "folder": d.source.split('/')[0] if '/' in d.source else "root",
                    "keywords": [], # Keywords now managed at chunks/metadata level
                    "topic": d.scope or "general",
                    "priority": 5,
                    "specificity": "medium",
                    "curated": True,
                    "id": d.id
                }
                for d in docs
            }
        finally:
            db.close()

    def sync_with_db(self):
        """Sync discovered files with database entries and remove stale ones"""
        if not self.auto_discovery or not self.domain_id:
            return
            
        discovered = self.auto_discovery.discover_all()
        db = SessionLocal()
        try:
            # 1. Add new or update existing
            for filename, metadata in discovered.items():
                doc = db.query(Document).filter_by(domain_id=self.domain_id, source=filename).first()
                if not doc:
                    print(f"🆕 Syncing new document to DB: {filename}")
                    doc = Document(
                        domain_id=self.domain_id,
                        title=metadata.get("name", filename),
                        source=filename,
                        version=metadata.get("version", "1.0.0"),
                        scope=metadata.get("topic", "public")
                    )
                    db.add(doc)
            
            # 2. Cleanup stale entries (documents in DB but not on disk)
            db_docs = db.query(Document).filter_by(domain_id=self.domain_id).all()
            for doc in db_docs:
                if doc.source not in discovered:
                    print(f"🗑️ Removing stale document from DB: {doc.source}")
                    # Chunks will be deleted via cascade if set up in SQLAlchemy, 
                    # but let's be safe if they aren't.
                    db.delete(doc)

            db.commit()
            self._load_from_db()
        except Exception as e:
            print(f"❌ Failed to sync discovery with DB: {e}")
            db.rollback()
        finally:
            db.close()
    
    def reload_if_changed(self):
        """Reload documents if any files have changed"""
        if self.auto_discovery and self.auto_discovery.has_changes():
            print("🔄 Changes detected, syncing with DB...")
            self.sync_with_db()
            return True
        return False
    
    def get_new_files(self) -> List[str]:
        """Get list of newly added files"""
        if not self.auto_discovery:
            return []
        
        known_files = list(self.documents.keys())
        return self.auto_discovery.get_new_files(known_files)
    
    def get_document(self, doc_name: str) -> Optional[Dict[str, Any]]:
        """Return metadata of a document"""
        return self.documents.get(doc_name)
    
    def get_docs_by_topic(self, topic: str) -> List[str]:
        """Return all documents of a topic"""
        return [name for name, info in self.documents.items() 
                if info["topic"] == topic]
    
    def get_docs_by_keyword(self, keyword: str) -> List[str]:
        """Return documents containing a keyword"""
        # Note: Keyword search is now primarily done via semantic search in RetrievalEngine
        return [name for name, info in self.documents.items()] 
    
    def get_all_docs(self) -> List[str]:
        """Return all documents"""
        return list(self.documents.keys())
    
    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        return {
            "total_documents": len(self.documents),
            "topics": list(set(doc["topic"] for doc in self.documents.values())),
            "auto_discovery_enabled": self.auto_discovery is not None,
            "domain_id": self.domain_id
        }

if __name__ == "__main__":
    # Test with a mock or existing domain_id
    kb = KnowledgeBase(domain_id="test-domain", enable_auto_discovery=True)
    print(kb.get_stats())
