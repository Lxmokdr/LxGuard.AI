import sys
import os

# Add the vendor_platform/api directory to path if needed (but this script is intended to run inside the container)
try:
    from database import SessionLocal
    from models import AdminUser
    from auth import hash_password

    db = SessionLocal()
    email = "admin@admin.com"
    password = "admin"

    user = db.query(AdminUser).filter(AdminUser.email == email).first()
    if user:
        user.password_hash = hash_password(password)
        print(f"Updated password for {email}")
    else:
        user = AdminUser(email=email, password_hash=hash_password(password))
        db.add(user)
        print(f"Created new admin: {email}")

    db.commit()
    print("✅ Success! You can now log in with:")
    print(f"Email: {email}")
    print(f"Password: {password}")

except Exception as e:
    print(f"❌ Error: {e}")
    print("\nNote: This script must be run INSIDE the vendor-api container.")
