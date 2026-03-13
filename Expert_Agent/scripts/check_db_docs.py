
import os
import sys
from sqlalchemy.orm import Session
from sqlalchemy import text

# Add project root to path
sys.path.append(os.getcwd())

from data.database import SessionLocal
from api.models import Document, Domain

def check_docs():
    db = SessionLocal()
    try:
        print("🔍 Checking Domains...")
        domains = db.query(Domain).all()
        for d in domains:
            print(f"  Domain: {d.name} (ID: {d.id})")
            
        print("\n🔍 Checking Documents...")
        docs = db.query(Document).all()
        print(f"Total Documents in DB: {len(docs)}")
        for d in docs:
            print(f"  Doc: {d.title} | Source: {d.source} | Domain: {d.domain_id}")
            
        print("\n🔍 Checking for Sanofi specifically...")
        sanofi = db.query(Document).filter(Document.title.ilike('%Sanofi%')).all()
        if sanofi:
            for s in sanofi:
                print(f"  ✅ Found: {s.title} (ID: {s.id}, Domain: {s.domain_id})")
        else:
            print("  ❌ No Sanofi document found in DB.")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_docs()
