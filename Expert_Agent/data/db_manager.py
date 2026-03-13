import sqlite3
import os
import logging
from datetime import datetime
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DBManager")

class DBManager:
    def __init__(self, db_path=None, schema_path=None):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.db_path = db_path or os.path.join(base_dir, "audit_db", "governance.db")
        self.schema_path = schema_path or os.path.join(base_dir, "schema.sql")
        
        self._ensure_db_dir()

    def _ensure_db_dir(self):
        directory = os.path.dirname(self.db_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

    def initialize_db(self):
        """Creates tables using schema.sql"""
        if not os.path.exists(self.schema_path):
            logger.error(f"Schema file not found at {self.schema_path}")
            return False

        try:
            with open(self.schema_path, 'r') as f:
                schema_script = f.read()

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.executescript(schema_script)
            conn.commit()
            conn.close()
            logger.info(f"Database initialized at {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize DB: {e}")
            return False

    def seed_data(self):
        """Seeds initial data (Admin User, etc.)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 1. Check if admin exists
            cursor.execute("SELECT user_id FROM users WHERE role='admin'")
            if cursor.fetchone():
                logger.info("Admin user already exists. Skipping seed.")
                conn.close()
                return

            # 2. Create Admin User
            admin_id = str(uuid.uuid4())
            cursor.execute(
                "INSERT INTO users (user_id, username, role) VALUES (?, ?, ?)",
                (admin_id, "admin", "admin")
            )
            
            # 3. Create Guest User
            guest_id = str(uuid.uuid4())
            cursor.execute(
                "INSERT INTO users (user_id, username, role) VALUES (?, ?, ?)",
                (guest_id, "guest_user", "guest")
            )

            # 4. Create Employee User
            emp_id = str(uuid.uuid4())
            cursor.execute(
                "INSERT INTO users (user_id, username, role) VALUES (?, ?, ?)",
                (emp_id, "employee_user", "employee")
            )

            conn.commit()
            conn.close()
            logger.info("Database seeded with default users (admin, guest, employee).")
            
        except Exception as e:
            logger.error(f"Failed to seed data: {e}")

if __name__ == "__main__":
    # Run as standalone script
    manager = DBManager()
    if manager.initialize_db():
        manager.seed_data()
