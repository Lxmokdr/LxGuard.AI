import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Database URL configuration
# Priority: SUPABASE_DB_URL > DATABASE_URL > Environment Variables > Local Docker Postgres
DB_URL = os.getenv("SUPABASE_DB_URL") or os.getenv("DATABASE_URL")

if not DB_URL:
    POSTGRES_USER = os.getenv("POSTGRES_USER", "hybrid")
    POSTGRES_PASS = os.getenv("POSTGRES_PASSWORD", "hybridpass")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5434")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "hybrid_db")
    DB_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASS}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Create Engine
engine = create_engine(DB_URL)

# Configure Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db():
    """ Dependency for getting a database session. """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
