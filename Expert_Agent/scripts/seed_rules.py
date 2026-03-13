import os
import sys

# Add project root to path to allow imports from other modules
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from sqlalchemy.orm import Session
from data.database import SessionLocal, engine, Base
from api.models import Intent, Rule, Domain
import yaml

def seed():
    db = SessionLocal()
    try:
        # 0. Get Domain ID (Default or created if missing)
        domain = db.query(Domain).filter(Domain.name.ilike("%Anti-Fraud%")).first()
        if not domain:
            domain = db.query(Domain).first()
        
        domain_id = domain.id if domain else "529af299-a716-44a0-b2ea-a262a501982f"
        print(f"📍 Using Domain: {domain.name if domain else 'Default'} ({domain_id})")

        # 1. Define Anti-Fraud Intents (Mapping AML-FRD-009 / Anti-Fraud.md Layer 1)
        intents_data = [
            {
                "name": "AML_TransactionMonitoring", 
                "domain_id": domain_id,
                "risk_level": "high", 
                "requires_approval": True, 
                "audit_level": "comprehensive", 
                "priority": 9, 
                "description": "Monitoring transactions for fraud and laundering (Indicator 2.1)",
                "keywords": ["deposit", "transfer", "transaction", "cash", "international", "jurisdiction", " structuring"],
                "verbs": ["monitor", "report", "flag", "check", "verify"],
                "confidence_boost": 0.2
            },
            {
                "name": "AML_BehavioralAnalysis", 
                "domain_id": domain_id,
                "risk_level": "high", 
                "requires_approval": True, 
                "audit_level": "comprehensive", 
                "priority": 8, 
                "description": "Analyzing customer/employee behavior for compliance (Indicator 2.2)",
                "keywords": ["behavior", "signatory", "ownership", "refusal", "source of funds", "beneficial"],
                "verbs": ["refuse", "avoid", "change", "suspect"],
                "confidence_boost": 0.15
            },
            {
                "name": "AML_STR_Submission", 
                "domain_id": domain_id,
                "risk_level": "critical", 
                "requires_approval": True, 
                "audit_level": "full", 
                "priority": 10, 
                "description": "Suspicious Transaction Report (STR) procedure (Section 5)",
                "keywords": ["STR", "report", "regulator", "procedure", "portal", "freeze"],
                "verbs": ["submit", "gather", "document", "attach"],
                "confidence_boost": 0.25
            },
            {
                "name": "AML_InternalFraud", 
                "domain_id": domain_id,
                "risk_level": "critical", 
                "requires_approval": True, 
                "audit_level": "full", 
                "priority": 10, 
                "description": "Monitoring internal misconduct (Section 6)",
                "keywords": ["employee", "misconduct", "hr", "criminal", "suspension", "audit"],
                "verbs": ["investigate", "suspend", "complain"],
                "confidence_boost": 0.2
            },
            {
                "name": "KnowledgeQuery", 
                "domain_id": domain_id,
                "risk_level": "low", 
                "requires_approval": False, 
                "audit_level": "standard", 
                "priority": 5, 
                "description": "General discovery of Anti-Fraud policy",
                "keywords": ["policy", "effective date", "department", "compliance", "rules"],
                "verbs": ["what", "how", "list"],
                "confidence_boost": 0.1
            }
        ]

        intent_map = {}
        for intent_info in intents_data:
            intent = db.query(Intent).filter(Intent.name == intent_info["name"]).first()
            if not intent:
                intent = Intent(**intent_info)
                db.add(intent)
                db.flush() # Get ID
                print(f"✅ Intent created: {intent.name}")
            else:
                # Update existing intent metadata
                for key, value in intent_info.items():
                    setattr(intent, key, value)
                print(f"🔄 Intent updated: {intent.name}")
            intent_map[intent.name] = intent.id

        # 2. Define Anti-Fraud Rules (Section 3 & 6 of Anti-Fraud.md)
        rules_data = [
            {
                "name": "RULE_A1_CashDeposits",
                "intent_name": "AML_TransactionMonitoring",
                "condition": ["cash deposits", "deposits > 1,000,000"],
                "action": {"alert_level": 1, "message": "Flag Level 1 alert for branch review."},
                "priority": 10,
                "description": "Flag cash deposits > 3x monthly average or > 1M DZD",
                "required_roles": ["employee", "admin"],
                "test_query": "I want to report a large cash deposit of 2 million DZD",
                "trigger_keywords": ["cash deposit", "large deposit", "1M DZD"]
            },
            {
                "name": "RULE_B2_InternationalTransfer",
                "intent_name": "AML_TransactionMonitoring",
                "condition": ["international transfer", "foreign transfer"],
                "action": {"alert_level": 2, "message": "Level 2 alert: Compliance review required."},
                "priority": 10,
                "description": "Flag transfers > 5M DZD to high-risk jurisdictions",
                "required_roles": ["employee", "admin"],
                "test_query": "How do I process an international transfer to a high risk country?",
                "trigger_keywords": ["international transfer", "foreign transfer", "high-risk jurisdiction"]
            },
            {
                "name": "RULE_C3_DormantAccount",
                "intent_name": "AML_TransactionMonitoring",
                "condition": ["dormant", "sudden inflow"],
                "action": {"action": "escalate", "message": "Escalate to Financial Crime Unit (Level 3)."},
                "priority": 9,
                "description": "Flag dormant account > 12m with sudden inflow > 2M DZD",
                "required_roles": ["employee", "admin"],
                "test_query": "What happens if a dormant account suddenly receives a lot of money?",
                "trigger_keywords": ["dormant account", "sudden inflow", "reactivated account"]
            },
            {
                "name": "RULE_STR_Procedure",
                "intent_name": "AML_STR_Submission",
                "condition": ["STR", "report submission"],
                "action": {"steps": ["Gather logs", "Document rationale", "Submit to portal"], "message": "Following Section 5 procedure."},
                "priority": 10,
                "description": "Suspicious Transaction Report mandatory submission flow",
                "required_roles": ["admin"],
                "test_query": "How do I submit an STR report?",
                "trigger_keywords": ["submit STR", "STR report", "suspicious transaction report"]
            },
            {
                "name": "RULE_AML_InternalFraud",
                "intent_name": "AML_InternalFraud",
                "condition": ["employee misconduct", "internal fraud"],
                "action": {"action": "suspend", "message": "Immediate system suspension and HR disciplinary action triggered."},
                "priority": 10,
                "description": "Immediate suspension for employee misconduct (Section 6)",
                "required_roles": ["admin"],
                "test_query": "What are the consequences of employee misconduct?",
                "trigger_keywords": ["internal fraud", "employee misconduct", "disciplinary action"]
            },
            {
                "name": "Audit all Critical Security Actions",
                "intent_name": "AML_InternalFraud", # Grouped under Internal Fraud for monitoring
                "condition": ["Security", "AccessChange"],
                "action": {"log": True, "audit": True, "message": "Critical security action captured in audit trail."},
                "priority": 10,
                "description": "Ensures all security actions are logged",
                "required_roles": [],
                "test_query": "How is security access changed and audited?",
                "trigger_keywords": ["security audit", "access change", "critical action"]
            }
        ]

        # 2.1 Cleanup "Old" Intents that don't belong to the Anti-Fraud scope
        legacy_intents = ["ImplementationPlanning", "FrontEndDesign", "GeneralQuery", "ExpertSystemDiscovery"]
        deleted_count = db.query(Intent).filter(Intent.name.in_(legacy_intents)).delete(synchronize_session=False)
        if deleted_count:
            print(f"🧹 Cleaned up {deleted_count} legacy intents.")

        for rule_info in rules_data:
            intent_name = rule_info.get("intent_name")
            intent_id = intent_map.get(intent_name)
            
            if not intent_id:
                print(f"⚠️ Warning: Intent {intent_name} not found for rule {rule_info['name']}. Skipping.")
                continue

            rule = db.query(Rule).filter(Rule.name == rule_info["name"]).first()
            if not rule:
                new_rule = Rule(
                    name=rule_info["name"],
                    domain_id=domain_id,
                    description=rule_info.get("description", ""),
                    intent_id=intent_id,
                    condition=rule_info.get("condition", []),
                    action=rule_info.get("action", {}),
                    priority=rule_info.get("priority", 5),
                    required_roles=rule_info.get("required_roles", []),
                    test_query=rule_info.get("test_query"),
                    trigger_keywords=rule_info.get("trigger_keywords", []),
                    active=True
                )
                db.add(new_rule)
                print(f"✅ Created Rule: {new_rule.name}")
            else:
                # Update existing rule
                rule.intent_id = intent_id
                rule.domain_id = domain_id
                rule.description = rule_info.get("description", rule.description)
                rule.condition = rule_info.get("condition", rule.condition)
                rule.action = rule_info.get("action", rule.action)
                rule.priority = rule_info.get("priority", rule.priority)
                rule.required_roles = rule_info.get("required_roles", rule.required_roles)
                rule.test_query = rule_info.get("test_query", rule.test_query)
                rule.trigger_keywords = rule_info.get("trigger_keywords", rule.trigger_keywords)
                print(f"🔄 Updated Rule: {rule.name}")
        
        db.commit()
        print("\n✨ Anti-Fraud Seeding completed successfully!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error during seeding: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed()
