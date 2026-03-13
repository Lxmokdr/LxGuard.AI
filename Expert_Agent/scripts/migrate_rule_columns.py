import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from data.database import engine
from sqlalchemy import text

def migrate():
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE rules ADD COLUMN IF NOT EXISTS test_query TEXT"))
            print("✅ Added column: test_query")
        except Exception as e:
            print(f"⚠️  test_query: {e}")
        
        try:
            conn.execute(text("ALTER TABLE rules ADD COLUMN IF NOT EXISTS trigger_keywords JSONB"))
            print("✅ Added column: trigger_keywords")
        except Exception as e:
            print(f"⚠️  trigger_keywords: {e}")
        
        conn.commit()
        print("✅ Migration complete")

if __name__ == "__main__":
    migrate()
