import sys
import os

# Add parent directory to path so we can import api modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.database import SessionLocal
from api.models import User
from api.auth import get_password_hash

def seed_users():
    db = SessionLocal()
    try:
        users_to_add = [
            {"id": "user-admin", "username": "admin", "password_hash": get_password_hash("admin123"), "role": "admin", "is_active": True},
            {"id": "user-employee", "username": "employee", "password_hash": get_password_hash("employee123"), "role": "employee", "is_active": True},
            {"id": "user-guest", "username": "guest", "password_hash": get_password_hash("guest123"), "role": "guest", "is_active": True}
        ]
        
        for user_data in users_to_add:
            existing_user = db.query(User).filter(User.username == user_data["username"]).first()
            if not existing_user:
                new_user = User(**user_data)
                db.add(new_user)
                print(f"Added user: {user_data['username']}")
            else:
                existing_user.password_hash = user_data["password_hash"]
                existing_user.role = user_data["role"]
                print(f"Updated user: {user_data['username']}")
        
        db.commit()
        print("Users seeded successfully!")
    except Exception as e:
        print(f"Error seeding users: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_users()
