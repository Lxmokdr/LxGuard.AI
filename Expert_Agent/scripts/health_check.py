
import os
import sys
import requests
from sqlalchemy.orm import Session
from sqlalchemy import text

# Add project root to path
sys.path.append(os.getcwd())

from data.database import SessionLocal
from api.models import User, Domain, Document, DocumentChunk

def health_check():
    db = SessionLocal()
    print("🏥 Starting Backend Health Check...")
    
    try:
        # 1. Check Database Connection & Tables
        print("\n📊 Database Status:")
        try:
            user_count = db.query(User).count()
            print(f"  ✅ Users: {user_count}")
            doc_count = db.query(Document).count()
            print(f"  ✅ Documents: {doc_count}")
            chunk_count = db.query(DocumentChunk).count()
            print(f"  ✅ Chunks: {chunk_count}")
        except Exception as e:
            print(f"  ❌ DB Query failed: {e}")

        # 2. Check User-Domain Mapping
        print("\n👤 User Mapping:")
        users = db.query(User).all()
        for u in users:
            domain_name = "None"
            if u.domain_id:
                domain = db.query(Domain).filter_by(id=u.domain_id).first()
                domain_name = domain.name if domain else "Unknown ID"
            print(f"  - User: {u.username} | Role: {u.role} | Domain: {domain_name} ({u.domain_id})")

        # 3. Check Ollama Connection
        print("\n🤖 Ollama Status:")
        ollama_host = os.getenv("OLLAMA_HOST", "http://ollama:11434")
        print(f"  Checking Ollama at: {ollama_host}")
        try:
            resp = requests.get(f"{ollama_host}/api/tags", timeout=5)
            if resp.status_code == 200:
                models = [m['name'] for m in resp.json().get('models', [])]
                print(f"  ✅ Ollama is UP. Available models: {', '.join(models)}")
            else:
                print(f"  ❌ Ollama returned status {resp.status_code}")
        except Exception as e:
            print(f"  ❌ Ollama connection failed: {e}")

        # 4. Check for Sanofi Doc Chunks specifically
        print("\n🔍 Document Inspection:")
        sanofi = db.query(Document).filter(Document.title.ilike('%Sanofi%')).first()
        if sanofi:
            chunks = db.query(DocumentChunk).filter_by(document_id=sanofi.id).count()
            print(f"  ✅ Sanofi document found (ID: {sanofi.id}) with {chunks} chunks.")
        else:
            print("  ❌ Sanofi document not found in DB.")

    finally:
        db.close()

if __name__ == "__main__":
    health_check()
