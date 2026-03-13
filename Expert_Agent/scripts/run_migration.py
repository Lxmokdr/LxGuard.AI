
import os
import sys
from sqlalchemy import text
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from data.database import SessionLocal, engine

def run_migration():
    print("🚀 Starting migration...")
    migration_path = Path(__file__).parent.parent / "data" / "fix_chunks_schema.sql"
    
    if not migration_path.exists():
        print(f"❌ Migration file not found: {migration_path}")
        return

    with open(migration_path, "r") as f:
        sql = f.read()

    try:
        with engine.connect() as conn:
            # We need to execute the script. 
            # Since it contains multiple statements, we split by ';' or just use text(sql) if it's one block.
            # CASCADE might be tricky in one go if psql vs sqlalchemy.
            # Let's execute the whole block.
            print("📜 Executing SQL...")
            conn.execute(text(sql))
            conn.commit()
            print("✅ Migration successful!")
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_migration()
