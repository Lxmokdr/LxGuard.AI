import yaml
import os
from typing import Dict, List, Any, Optional
from data.database import SessionLocal
from api.models import Intent, Rule, OntologyEntity, PromptTemplate, AnswerMode, JsonSchema

class RuleLoader:
    """
    Loads expert rules, ontology, and templates from the database.
    """
    
    def __init__(self, domain_id: str = None):
        self.domain_id = domain_id
        self.config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
        
    def load_intents(self, domain_id: str = None) -> List[Dict[str, Any]]:
        """Load intents from database"""
        target_domain = domain_id or self.domain_id
        
        db = SessionLocal()
        try:
            # If domain_id is provided, filter by it. Otherwise get all.
            query = db.query(Intent)
            if target_domain:
                query = query.filter_by(domain_id=target_domain)
            
            intents = query.all()
            return [
                {
                    "name": i.name,
                    "description": i.description,
                    "risk_level": i.risk_level,
                    "requires_approval": i.requires_approval,
                    "audit_level": i.audit_level,
                    "confidence_threshold": i.confidence_threshold,
                    "structured_output_required": i.structured_output_required
                }
                for i in intents
            ]
        finally:
            db.close()
        
    def load_ontology(self, domain_id: str = None) -> List[Dict[str, Any]]:
        """Load ontology from database"""
        target_domain = domain_id or self.domain_id
        if not target_domain:
            return []
            
        db = SessionLocal()
        try:
            entities = db.query(OntologyEntity).filter_by(domain_id=target_domain).all()
            return [
                {
                    "name": e.name,
                    "parent": db.query(OntologyEntity).get(e.parent_id).name if e.parent_id else None,
                    "requires": e.requires or [],
                    "excludes": e.excludes or [],
                    "priority": e.priority,
                    "specificity": e.specificity
                }
                for e in entities
            ]
        finally:
            db.close()
            
    def load_rules(self, domain_id: str = None) -> List[Dict[str, Any]]:
        """Load rules from database"""
        target_domain = domain_id or self.domain_id
        if not target_domain:
            return []
            
        db = SessionLocal()
        try:
            rules = db.query(Rule).filter_by(domain_id=target_domain).all()
            return [
                {
                    "name": r.name,
                    "condition": r.condition or [],
                    "action": r.action or {},
                    "priority": r.priority,
                    "description": r.description,
                    "required_roles": r.required_roles or [],
                    "test_query": r.test_query,
                    "trigger_keywords": r.trigger_keywords or []
                }
                for r in rules
            ]
        finally:
            db.close()
            
    def load_templates(self, domain_id: str = None) -> Dict[str, Any]:
        """Load answer templates from database (PromptTemplates)"""
        target_domain = domain_id or self.domain_id
        if not target_domain:
            return {}
            
        db = SessionLocal()
        try:
            prompts = db.query(PromptTemplate).filter_by(domain_id=target_domain).all()
            templates = {}
            for p in prompts:
                # Find intent name
                intent = db.query(Intent).get(p.intent_id) if p.intent_id else None
                intent_name = intent.name if intent else "General"
                
                # Try to parse structure from body (mocking the YAML structure for compatibility)
                # In the future, this should be a proper JSON field in PromptTemplate
                templates[intent_name] = {
                    "template": p.template_body,
                    "version": p.version
                }
            return templates
        finally:
            db.close()
            
    def load_json_schema(self, schema_name: str, domain_id: str = None) -> Optional[Dict[str, Any]]:
        """Load JSON schema from database"""
        target_domain = domain_id or self.domain_id
        if not target_domain:
            return None
            
        db = SessionLocal()
        try:
            from api.models import JsonSchema
            schema = db.query(JsonSchema).filter_by(domain_id=target_domain, name=schema_name).first()
            return schema.schema_definition if schema else None
        finally:
            db.close()

if __name__ == "__main__":
    # Test loader
    loader = RuleLoader()
    print(f"Ontology: {len(loader.load_ontology())} concepts")
    print(f"Rules: {len(loader.load_rules())} rules")
    print(f"Templates: {len(loader.load_templates())} templates")
