import os
import sys

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.database import engine
from sqlalchemy import text

def list_tables():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
        for row in result:
            print(f"Table: {row[0]}")

if __name__ == "__main__":
    list_tables()
