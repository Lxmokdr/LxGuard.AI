import os
import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from sqlalchemy.orm import Session
from data.database import SessionLocal
from api.models import Document, Domain
from services.document_indexing import reindex_document, remove_document
from services.ontology_service import build_ontology

class KnowledgeSyncHandler(FileSystemEventHandler):
    """
    Event handler that triggers indexing and ontology rebuilds
    when files in the documents directory change.
    """
    def __init__(self, app_state, source_dir):
        self.app_state = app_state
        self.source_dir = source_dir
        self.last_sync = 0
        self.sync_cooldown = 2 # seconds

    def _should_sync(self):
        return (time.time() - self.last_sync) > self.sync_cooldown

    def on_modified(self, event):
        if not event.is_directory and event.src_path.lower().endswith(('.pdf', '.md', '.txt')):
            print(f"🔄 File modified: {event.src_path}. Syncing...")
            self._trigger_sync(event.src_path)

    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith(('.pdf', '.md', '.txt')):
            print(f"🆕 File created: {event.src_path}. Syncing...")
            self._trigger_sync(event.src_path)

    def on_deleted(self, event):
        if not event.is_directory and event.src_path.lower().endswith(('.pdf', '.md', '.txt')):
            print(f"🗑 File deleted: {event.src_path}. Syncing...")
            self._handle_deletion(os.path.basename(event.src_path))

    def _trigger_sync(self, filepath):
        if not self._should_sync():
            return
        
        db = SessionLocal()
        try:
            filename = os.path.basename(filepath)
            # Find or create document entry
            doc = db.query(Document).filter(Document.source == filename).first()
            if not doc:
                first_domain = db.query(Domain).first()
                domain_id = first_domain.id if first_domain else None
                doc = Document(
                    source=filename,
                    title=filename,
                    domain_id=domain_id,
                    scope="internal"
                )
                db.add(doc)
                db.commit()
                db.refresh(doc)
            
            # Reindex
            reindex_document(db, doc, self.source_dir)
            
            # Rebuild Ontology
            build_ontology(self.source_dir, self.app_state)
            
            self.last_sync = time.time()
            print(f"✅ Sync complete for {filename}")
        except Exception as e:
            print(f"❌ Error during auto-sync for {filepath}: {e}")
        finally:
            db.close()

    def _handle_deletion(self, filename):
        db = SessionLocal()
        try:
            remove_document(db, filename)
            # Rebuild Ontology after deletion
            build_ontology(self.source_dir, self.app_state)
            print(f"✅ Removal and ontology refresh complete for {filename}")
        except Exception as e:
            print(f"❌ Error during deletion sync for {filename}: {e}")
        finally:
            db.close()

def perform_initial_indexing(source_dir: str):
    """
    Check all documents in the database and index those with 0 chunks.
    This ensures that documents present at startup are searchable.
    """
    from api.models import Document, DocumentChunk
    db = SessionLocal()
    try:
        docs = db.query(Document).all()
        print(f"🔍 [Startup] Checking indexing status for {len(docs)} documents...", flush=True)
        
        indexed_count = 0
        for doc in docs:
            chunk_count = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).count()
            if chunk_count == 0:
                print(f"🏗️  [Startup] Document '{doc.source}' has 0 chunks. Performing INITIAL INDEXING...", flush=True)
                try:
                    reindex_document(db, doc, source_dir)
                    indexed_count += 1
                except Exception as e:
                    print(f"❌ [Startup] Failed to index {doc.source}: {e}", flush=True)
            else:
                # print(f"✅ [Startup] Document '{doc.source}' already has {chunk_count} chunks.", flush=True)
                pass
        
        if indexed_count > 0:
            print(f"✅ [Startup] Initial indexing complete. {indexed_count} documents indexed.", flush=True)
        else:
            print(f"✅ [Startup] All documents already indexed.", flush=True)
            
    except Exception as e:
        print(f"❌ [Startup] Error during initial indexing pass: {e}", flush=True)
    finally:
        db.close()

def start_knowledge_sync(app_state):
    """
    Initializes and starts the file system watcher in a background thread.
    """
    source_dir = getattr(app_state, 'admin_config', {}).get('source_directory', 'docs')
    
    # Ensure source directory exists
    if not os.path.exists(source_dir):
        os.makedirs(source_dir, exist_ok=True)
        
    print(f"🔭 Starting Knowledge Sync Watcher on: {os.path.abspath(source_dir)}")
    
    # --- Perform initial indexing pass for existing documents ---
    perform_initial_indexing(source_dir)
    
    event_handler = KnowledgeSyncHandler(app_state, source_dir)
    observer = Observer()
    observer.schedule(event_handler, source_dir, recursive=True)
    
    def run_observer():
        observer.start()
        try:
            # Wait until the observer is explicitly stopped
            while observer.is_alive():
                observer.join(1)
        except Exception as e:
            print(f"🛑 Watcher crashed: {e}")
            observer.stop()
            observer.join()

    # Run in background daemon thread
    watcher_thread = threading.Thread(target=run_observer, daemon=True)
    watcher_thread.start()
    return observer
