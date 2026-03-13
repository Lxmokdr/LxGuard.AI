"""
Vendor Platform Database Configuration
Completely separate from enterprise deployments.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

VENDOR_DB_URL = os.environ.get(
    "VENDOR_DATABASE_URL",
    "postgresql://vendor:vendorpass@vendor_db:5432/vendor_db"
)

engine = create_engine(VENDOR_DB_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
