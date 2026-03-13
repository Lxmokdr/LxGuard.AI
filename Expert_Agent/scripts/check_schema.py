
import os
import sys
from sqlalchemy import text
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from data.database import SessionLocal, engine

def check_schema():
    print("🔍 Checking document_chunks table schema...")
    with engine.connect() as conn:
        # Check columns
        result = conn.execute(text("""
            SELECT column_name, data_type, character_maximum_length 
            FROM information_schema.columns 
            WHERE table_name = 'document_chunks';
        """))
        columns = result.fetchall()
        print("\nColumns in 'document_chunks':")
        for col in columns:
            print(f"  - {col[0]}: {col[1]}")
            
        # Check vector dimension specifically
        try:
            result = conn.execute(text("""
                SELECT atttypmod 
                FROM pg_attribute 
                WHERE attrelid = 'document_chunks'::regclass 
                AND attname = 'embedding';
            """))
            typmod = result.fetchone()
            if typmod and typmod[0] != -1:
                print(f"\nVector Dimension: {typmod[0]}")
            else:
                print("\nVector Dimension: not constrained or not found")
        except Exception as e:
            print(f"\nError checking vector dimension: {e}")

if __name__ == "__main__":
    check_schema()
