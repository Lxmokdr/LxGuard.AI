
import os
import sys
from sqlalchemy.orm import Session

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.database import SessionLocal
from api.models import User

def check_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print(f"Total Users: {len(users)}")
        for u in users:
            print(f"ID: {u.id} | Username: {u.username} | Role: {u.role} | Has Pass: {bool(u.password_hash)}")
    finally:
        db.close()

if __name__ == "__main__":
    check_users()
