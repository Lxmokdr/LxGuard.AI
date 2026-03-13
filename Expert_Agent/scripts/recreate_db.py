import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.database import engine, Base
import api.models  # Ensure all models are registered

def recreate():
    print("🔥 Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("✨ Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database schema synchronized with models!")

if __name__ == "__main__":
    recreate()
