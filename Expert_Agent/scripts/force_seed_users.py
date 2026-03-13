
import sys
import os
import uuid
from datetime import datetime

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from data.database import SessionLocal, engine
from api.models import User
from api.auth import get_password_hash

from scripts.fix_db_schema import fix_schema

def force_seed():
    # 1. Ensure schema is correct
    fix_schema()
    
    db = SessionLocal()
    try:
        # 2. Get Domain
        from api.models import Domain
        domain = db.query(Domain).filter_by(name="Next.js Development").first()
        domain_id = domain.id if domain else None
        
        if not domain_id:
            print("⚠️  Warning: 'Next.js Development' domain not found. Users will have no domain_id.")

        # 3. Create/Update users
        users_data = [
            {
                "id": "1",
                "username": "admin",
                "email": "admin@expert-agent.ai",
                "role": "admin",
                "password": "admin123",
                "domain_id": domain_id
            },
            {
                "id": "2",
                "username": "employee",
                "email": "john.doe@enterprise.com",
                "role": "employee",
                "password": "employee123",
                "domain_id": domain_id
            },
            {
                "id": "guest",
                "username": "guest",
                "email": "guest@public.com",
                "role": "guest",
                "password": "guest123",
                "domain_id": domain_id
            }
        ]

        for u_data in users_data:
            user = db.query(User).filter(User.username == u_data["username"]).first()
            if user:
                print(f"🔄 Updating existing user: {user.username}")
                user.password_hash = get_password_hash(u_data["password"])
                user.role = u_data["role"]
                user.domain_id = u_data.get("domain_id")
                user.is_active = True
            else:
                print(f"✅ Creating new user: {u_data['username']}")
                user = User(
                    id=u_data["id"],
                    username=u_data["username"],
                    email=u_data["email"],
                    role=u_data["role"],
                    domain_id=u_data.get("domain_id"),
                    password_hash=get_password_hash(u_data["password"]),
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                db.add(user)
            
            db.commit()

        print("\n✨ Force user seeding completed successfully!")

    except Exception as e:
        print(f"❌ Error during force seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    force_seed()
