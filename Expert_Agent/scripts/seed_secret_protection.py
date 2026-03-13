import os
import sys

# Add project root to path to allow imports from other modules
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from sqlalchemy.orm import Session
from data.database import SessionLocal, engine, Base
from api.models import Intent, Rule, Domain

def seed():
    db = SessionLocal()
    try:
        # 1. Get Domain ID
        domain = db.query(Domain).first()
        if not domain:
            print("❌ No domain found. Please create a domain first.")
            return
        
        domain_id = domain.id
        print(f"📍 Using Domain: {domain.name} ({domain_id})")

        # 2. Create ConfidentialQuery Intent
        intent_name = "ConfidentialQuery"
        intent = db.query(Intent).filter(Intent.name == intent_name).first()
        
        intent_info = {
            "name": intent_name,
            "domain_id": domain_id,
            "risk_level": "high",
            "requires_approval": True,
            "audit_level": "comprehensive",
            "priority": 10,
            "description": "Questions about sensitive or confidential information like secrets",
            "keywords": ["secret", "coffee", "confidential", "private"],
            "verbs": ["tell", "reveal", "show", "what is"],
            "confidence_boost": 0.3
        }
        
        if not intent:
            intent = Intent(**intent_info)
            db.add(intent)
            db.flush()
            print(f"✅ Intent created: {intent.name}")
        else:
            for key, value in intent_info.items():
                setattr(intent, key, value)
            print(f"🔄 Intent updated: {intent.name}")
        
        intent_id = intent.id

        # 3. Create RULE_SECRET_PROTECTION
        rule_name = "RULE_SECRET_PROTECTION"
        rule = db.query(Rule).filter(Rule.name == rule_name).first()
        
        rule_info = {
            "name": rule_name,
            "domain_id": domain_id,
            "intent_id": intent_id,
            "description": "Blocks revelation of secrets like 'coffee'",
            "condition": ["secret", "coffee"],
            "action": {
                "topic": "security",
                "forbidden_docs": ["test.txt"],
                "message": "I am not authorized to reveal secret information."
            },
            "priority": 11,
            "required_roles": ["admin"],
            "test_query": "What is the secret?",
            "trigger_keywords": ["secret", "coffee"],
            "active": True
        }
        
        if not rule:
            rule = Rule(**rule_info)
            db.add(rule)
            print(f"✅ Created Rule: {rule.name}")
        else:
            for key, value in rule_info.items():
                setattr(rule, key, value)
            print(f"🔄 Updated Rule: {rule.name}")
            
        db.commit()
        print("\n✨ Secret Protection seeding completed successfully!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error during seeding: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed()
