from api.database import SessionLocal
from api.models import Rule, Intent
import json

db = SessionLocal()
try:
    rules = db.query(Rule).all()
    print(f"Total rules: {len(rules)}")
    for r in rules:
        intent = db.query(Intent).filter(Intent.id == r.intent_id).first()
        intent_name = intent.name if intent else "Unknown"
        if "secret" in (r.name or "").lower() or "secret" in (r.trigger_keywords or []) or "secret" in (r.description or "").lower():
            print(f"--- Rule: {r.name} ---")
            print(f"ID: {r.id}")
            print(f"Intent: {intent_name}")
            print(f"Keywords: {r.trigger_keywords}")
            print(f"Active: {r.active}")
            print(f"Action: {r.action}")
            print(f"Excludes: {r.excludes}")
finally:
    db.close()
