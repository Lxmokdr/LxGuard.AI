
import os
import sys
from sqlalchemy import text
from sqlalchemy.orm import Session

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.database import engine, SessionLocal

def fix_schema():
    print("🛠 Checking database schema...")
    with engine.connect() as conn:
        # 1. Check if 'users' table has domain_id column
        result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='users' AND column_name='domain_id'"))
        if not result.fetchone():
            print("🚀 Adding 'domain_id' column to 'users' table...")
            conn.execute(text("ALTER TABLE users ADD COLUMN domain_id VARCHAR"))
            conn.commit()
            print("✅ 'domain_id' column added.")

        # 2. Check if 'documents' table has domain_id column
        result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='documents' AND column_name='domain_id'"))
        if not result.fetchone():
            print("🚀 Adding 'domain_id' column to 'documents' table...")
            conn.execute(text("ALTER TABLE documents ADD COLUMN domain_id VARCHAR"))
            conn.commit()
            print("✅ 'domain_id' column added.")

        # 3. Check if 'document_chunks' table has domain_id column
        result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='document_chunks' AND column_name='domain_id'"))
        if not result.fetchone():
            print("🚀 Adding 'domain_id' column to 'document_chunks' table...")
            conn.execute(text("ALTER TABLE document_chunks ADD COLUMN domain_id VARCHAR"))
            conn.commit()
            print("✅ 'domain_id' column added.")

        # 4. Check if 'intents' table has requires_approval column
        result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='intents' AND column_name='requires_approval'"))
        if not result.fetchone():
            print("🚀 Adding 'requires_approval' column to 'intents' table...")
            conn.execute(text("ALTER TABLE intents ADD COLUMN requires_approval BOOLEAN DEFAULT FALSE"))
            conn.commit()
            print("✅ 'requires_approval' column added.")

        # 5. Check if 'intents' table has audit_level column
        result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='intents' AND column_name='audit_level'"))
        if not result.fetchone():
            print("🚀 Adding 'audit_level' column to 'intents' table...")
            conn.execute(text("ALTER TABLE intents ADD COLUMN audit_level VARCHAR DEFAULT 'standard'"))
            conn.commit()
            print("✅ 'audit_level' column added.")

        # 6. Check if 'intents' table has priority column
        result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='intents' AND column_name='priority'"))
        if not result.fetchone():
            print("🚀 Adding 'priority' column to 'intents' table...")
            conn.execute(text("ALTER TABLE intents ADD COLUMN priority INTEGER DEFAULT 5"))
            conn.commit()
            print("✅ 'priority' column added.")

        # 7. Fix vector dimension for all-MiniLM-L6-v2 (384)
        print("📏 Adjusting embedding vector dimension to 384...")
        try:
            conn.execute(text("ALTER TABLE document_chunks ALTER COLUMN embedding TYPE vector(384)"))
            conn.commit()
            print("✅ Vector dimension set to 384.")
        except Exception as e:
            print(f"ℹ️ Could not adjust vector dimension (might already be set or has data): {e}")

if __name__ == "__main__":
    fix_schema()
