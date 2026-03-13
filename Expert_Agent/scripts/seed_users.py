import sys
import os
import uuid
from datetime import datetime

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from data.database import SessionLocal, engine, Base
from api.models import User
from api.auth import get_password_hash

def seed():
    db = SessionLocal()
    try:
        # Create users matching the mock auth system for consistency
        users_data = [
            {
                "id": "1",
                "username": "admin",
                "email": "admin@expert-agent.ai",
                "role": "admin",
                "password_hash": get_password_hash("admin123"),
                "is_active": True
            },
            {
                "id": "2",
                "username": "employee",
                "email": "john.doe@enterprise.com",
                "role": "employee",
                "password_hash": get_password_hash("employee123"),
                "is_active": True
            },
            {
                "id": "guest",
                "username": "guest",
                "email": "guest@public.com",
                "role": "guest",
                "password_hash": get_password_hash("guest123"),
                "is_active": True
            }
        ]

        for user_info in users_data:
            existing_user = db.query(User).filter(User.id == user_info["id"]).first()
            if not existing_user:
                user = User(
                    **user_info,
                    created_at=datetime.utcnow()
                )
                db.add(user)
                db.commit()
                print(f"✅ Created User: {user.username} ({user.role})")
            else:
                print(f"ℹ️ User already exists: {existing_user.username}")

        print("\n✨ User seeding completed successfully!")

    finally:
        db.close()

if __name__ == "__main__":
    seed()
