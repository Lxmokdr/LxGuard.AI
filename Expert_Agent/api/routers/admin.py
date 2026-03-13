from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks, File, UploadFile, Form
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
import uuid
import shutil
from sqlalchemy.orm import Session

from api.auth import get_current_user, User
from api.models import User as DBUser, Document as DBDocument, Intent as DBIntent, DocumentChunk as DBDocumentChunk
from data.database import get_db
from services.document_indexing import (
    reindex_document,
    DocumentFileNotFound,
    DocumentExtractionError,
    DocumentChunkingError,
)
from services.ontology_service import build_ontology

router = APIRouter(prefix="/admin", tags=["admin"])

# Global Admin Configuration (Shared via app meta or state)
# For simplicity in router, we access via request.app.state

# --- Models ---
class UserCreate(BaseModel):
    username: str
    role: str
    email: Optional[str] = None
    password: Optional[str] = None

class UserUpdate(BaseModel):
    role: Optional[str] = None
    is_active: Optional[bool] = None

class DirectoryConfig(BaseModel):
    path: str

class TripleActionRequest(BaseModel):
    subject: str
    predicate: str
    object: str
    action: str
    subject_uri: Optional[str] = None
    predicate_uri: Optional[str] = None
    object_uri: Optional[str] = None

class RuleCreateRequest(BaseModel):
    name: str  # Human readable name
    intent: str
    triggers: List[str]
    action: Dict[str, Any]
    priority: int = 5
    description: Optional[str] = None
    required_roles: List[str] = []
    test_query: Optional[str] = None
    trigger_keywords: List[str] = []

class IntentUpdate(BaseModel):
    risk_level: Optional[str] = None
    description: Optional[str] = None
    requires_approval: Optional[bool] = None
    audit_level: Optional[str] = None
    confidence_threshold: Optional[float] = None
    priority: Optional[int] = None

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    scope: Optional[str] = None
    access_level: Optional[str] = None

class SimulationRequest(BaseModel):
    query: str
    user_role: str
    context: Optional[Dict[str, Any]] = None
    intent_override: Optional[str] = None

class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None

class RuleStatusUpdate(BaseModel):
    active: bool

class RuleTestRequest(BaseModel):
    query: str
    user_role: str

# --- Endpoints ---

@router.get("/roles")
async def get_admin_roles(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != "admin": raise HTTPException(status_code=403, detail="Admin access required")
    # This would query the 'roles' table in schema.sql
    from api.models import Role as DBRole
    roles = db.query(DBRole).all()
    return roles

@router.post("/roles")
async def create_admin_role(new_role: RoleCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != "admin": raise HTTPException(status_code=403, detail="Admin access required")
    from api.models import Role as DBRole
    db_role = DBRole(name=new_role.name, description=new_role.description)
    db.add(db_role); db.commit(); db.refresh(db_role)
    return {"status": "created", "id": db_role.id}

@router.post("/seed-rules")
async def seed_rules(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    print(">>> SEED RULES ENDPOINT HIT")
    if user.role != "admin": raise HTTPException(status_code=403, detail="Admin access required")
    print(">>> ADMIN CHECK PASSED")
    
    try:
        from api.models import Intent as DBIntent, Rule as DBRule, Domain as DBDomain
        print(">>> MODELS IMPORTED SUCCESSFULLY")

        # Get or fallback to first domain
        domain = db.query(DBDomain).filter(DBDomain.name.ilike("%Anti-Fraud%")).first()
        if not domain:
            domain = db.query(DBDomain).first()
        domain_id = domain.id if domain else None
        
        intents_data = [
            {"name": "AML_TransactionMonitoring", "domain_id": domain_id, "risk_level": "high", "requires_approval": True, "audit_level": "comprehensive", "priority": 9, "description": "Monitoring transactions for fraud and laundering", "keywords": ["deposit", "transfer", "transaction", "cash", "international", "structuring"], "verbs": ["monitor", "report", "flag", "check", "verify"], "confidence_boost": 0.2},
            {"name": "AML_STR_Submission", "domain_id": domain_id, "risk_level": "critical", "requires_approval": True, "audit_level": "full", "priority": 10, "description": "Suspicious Transaction Report procedure", "keywords": ["STR", "report", "regulator", "procedure", "portal", "freeze"], "verbs": ["submit", "gather", "document", "attach"], "confidence_boost": 0.25},
            {"name": "AML_InternalFraud", "domain_id": domain_id, "risk_level": "critical", "requires_approval": True, "audit_level": "full", "priority": 10, "description": "Monitoring internal misconduct", "keywords": ["employee", "misconduct", "hr", "criminal", "suspension", "audit"], "verbs": ["investigate", "suspend", "complain"], "confidence_boost": 0.2},
        ]

        intent_map = {}
        for intent_info in intents_data:
            print(f">>> CHECKING INTENT: {intent_info['name']}")
            intent = db.query(DBIntent).filter(DBIntent.name == intent_info["name"]).first()
            if not intent:
                intent = DBIntent(**intent_info)
                db.add(intent)
                db.flush()
            else:
                for k, v in intent_info.items():
                    setattr(intent, k, v)
            intent_map[intent.name] = intent.id

        rules_data = [
            {"name": "RULE_A1_CashDeposits", "intent_name": "AML_TransactionMonitoring", "condition": ["cash deposits", "deposits > 1,000,000"], "action": {"alert_level": 1, "message": "Flag Level 1 alert for branch review."}, "priority": 10, "description": "Flag cash deposits > 3x monthly average or > 1M DZD", "required_roles": ["employee", "admin"], "test_query": "I want to report a large cash deposit of 2 million DZD", "trigger_keywords": ["cash deposit", "large deposit", "1M DZD"]},
            {"name": "RULE_B2_InternationalTransfer", "intent_name": "AML_TransactionMonitoring", "condition": ["international transfer", "foreign transfer"], "action": {"alert_level": 2, "message": "Level 2 alert: Compliance review required."}, "priority": 10, "description": "Flag transfers > 5M DZD to high-risk jurisdictions", "required_roles": ["employee", "admin"], "test_query": "How do I process an international transfer to a high risk country?", "trigger_keywords": ["international transfer", "foreign transfer", "high-risk jurisdiction"]},
            {"name": "RULE_C3_DormantAccount", "intent_name": "AML_TransactionMonitoring", "condition": ["dormant", "sudden inflow"], "action": {"action": "escalate", "message": "Escalate to Financial Crime Unit (Level 3)."}, "priority": 9, "description": "Flag dormant account > 12m with sudden inflow > 2M DZD", "required_roles": ["employee", "admin"], "test_query": "What happens if a dormant account suddenly receives a lot of money?", "trigger_keywords": ["dormant account", "sudden inflow", "reactivated account"]},
            {"name": "RULE_STR_Procedure", "intent_name": "AML_STR_Submission", "condition": ["STR", "report submission"], "action": {"steps": ["Gather logs", "Document rationale", "Submit to portal"], "message": "Following Section 5 procedure."}, "priority": 10, "description": "Suspicious Transaction Report mandatory submission flow", "required_roles": ["admin"], "test_query": "How do I submit an STR report?", "trigger_keywords": ["submit STR", "STR report", "suspicious transaction report"]},
            {"name": "RULE_AML_InternalFraud", "intent_name": "AML_InternalFraud", "condition": ["employee misconduct", "internal fraud"], "action": {"action": "suspend", "message": "Immediate system suspension and HR disciplinary action triggered."}, "priority": 10, "description": "Immediate suspension for employee misconduct", "required_roles": ["admin"], "test_query": "What are the consequences of employee misconduct?", "trigger_keywords": ["internal fraud", "employee misconduct", "disciplinary action"]},
            {"name": "Audit all Critical Security Actions", "intent_name": "AML_InternalFraud", "condition": ["Security", "AccessChange"], "action": {"log": True, "audit": True, "message": "Critical security action captured in audit trail."}, "priority": 10, "description": "Ensures all security actions are logged", "required_roles": [], "test_query": "How is security access changed and audited?", "trigger_keywords": ["security audit", "access change", "critical action"]},
        ]

        for rule_info in rules_data:
            intent_name = rule_info.pop("intent_name")
            intent_id = intent_map.get(intent_name)
            if not intent_id: continue

            existing_rule = db.query(DBRule).filter(DBRule.name == rule_info["name"]).first()
            if not existing_rule:
                rule = DBRule(domain_id=domain_id, intent_id=intent_id, **rule_info)
                db.add(rule)
            else:
                for k, v in rule_info.items():
                    setattr(existing_rule, k, v)
                existing_rule.intent_id = intent_id
                existing_rule.domain_id = domain_id
                
        db.commit()
        return {"status": "success", "message": "Anti-fraud rules seeded successfully with test queries."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to seed database: {str(e)}")

@router.get("/rules/conflicts")
async def get_rule_conflicts(req: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != "admin": raise HTTPException(status_code=403, detail="Admin access required")
    # TODO: Implement DB-backed rule conflict checking
    conflicts = []
    return {"conflicts": conflicts, "count": len(conflicts)}

@router.get("/compliance/export")
async def export_compliance_report(req: Request, format: str = "csv", user: User = Depends(get_current_user)):
    if user.role != "admin": raise HTTPException(status_code=403, detail="Admin access required")
    # This generates a compliance report (Enterprise maturity check)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"compliance_report_{timestamp}.{format}"
    # In a real app, this would return a StreamingResponse
    return {
        "status": "success",
        "filename": filename,
        "format": format,
        "summary": {
            "total_queries": 1500,
            "security_violations": 12,
            "rule_adherence": "99.2%"
        }
    }

@router.get("/audit/diff/{query_id}")
async def get_audit_diff(query_id: str, req: Request, user: User = Depends(get_current_user)):
    if user.role != "admin": raise HTTPException(status_code=403, detail="Admin access required")
    # Returns a diff between reasoning steps (Enterprise maturity check)
    return {
        "query_id": query_id,
        "diff_type": "intent_shift",
        "changes": [
            {"step": "Layer 3", "original": "General", "revised": "Deployment", "reason": "Rule matching boost"}
        ]
    }

@router.get("/users")
async def get_admin_users(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != "admin": raise HTTPException(status_code=403, detail="Admin access required")
    try:
        users = db.query(DBUser).all()
        return [{"id": u.id, "username": u.username, "role": u.role, "email": u.email, "is_active": u.is_active, "created_at": u.created_at.isoformat() if u.created_at else None} for u in users]
    except Exception as e:
        print(f"⚠️ Error fetching users: {e}")
        return []

@router.post("/users")
async def create_admin_user(new_user: UserCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != "admin": raise HTTPException(status_code=403, detail="Admin access required")
    
    password_hash = None
    if new_user.password:
        import hashlib
        password_hash = hashlib.sha256(new_user.password.encode()).hexdigest()
        
    db_user = DBUser(
        id=str(uuid.uuid4()), 
        username=new_user.username, 
        role=new_user.role, 
        email=new_user.email, 
        password_hash=password_hash,
        is_active=True, 
        created_at=datetime.utcnow()
    )
    db.add(db_user); db.commit(); db.refresh(db_user)
    
    # Securely auto-allocate an ApiRateLimit for the new user
    from api.models import ApiRateLimit
    rate_limit = ApiRateLimit(
        user_id=db_user.id,
        tenant_id=getattr(db_user, 'tenant_id', None),
        role=db_user.role,
        monthly_token_quota=1000000 if db_user.role == "admin" else 100000,
        daily_request_limit=10000 if db_user.role == "admin" else 1000,
        current_month_tokens=0,
        current_day_requests=0
    )
    db.add(rate_limit)
    db.commit()
    
    return {"status": "created", "id": db_user.id}
@router.put("/users/{user_id}")
async def update_admin_user(user_id: str, update_data: UserUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != "admin": raise HTTPException(status_code=403, detail="Admin access required")
    db_user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if update_data.role is not None:
        db_user.role = update_data.role
    if update_data.is_active is not None:
        db_user.is_active = update_data.is_active
        
    db.commit(); db.refresh(db_user)
    return {"status": "updated", "id": db_user.id}

@router.delete("/users/{user_id}")
async def delete_admin_user(user_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != "admin": raise HTTPException(status_code=403, detail="Admin access required")
    if user.id == user_id: raise HTTPException(status_code=400, detail="Cannot delete your own user account")
    
    db_user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Manually delete associated ApiRateLimit to satisfy FK constraints
    from api.models import ApiRateLimit
    db.query(ApiRateLimit).filter(ApiRateLimit.user_id == user_id).delete()
    
    db.delete(db_user)
    db.commit()
    return {"status": "deleted", "id": user_id}

@router.get("/documents")
async def get_admin_documents(req: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != "admin": raise HTTPException(status_code=403, detail="Admin access required")
    
    # Sync with DB to cleanup stale files if pipeline is ready
    pipeline = getattr(req.app.state, 'pipeline', None)
    if pipeline and hasattr(pipeline, 'kb'):
        try:
            pipeline.kb.sync_with_db()
        except Exception as e:
            print(f"⚠️ Sync failed during document fetch: {e}")

    source_dir = req.app.state.admin_config["source_directory"]
    
    db_docs = {}
    chunk_counts = {}
    try:
        db_docs = {d.source: d for d in db.query(DBDocument).all()}
        
        # Get actual chunk and vector counts grouped by document_id
        from sqlalchemy import func
        counts = db.query(
            DBDocumentChunk.document_id, 
            func.count(DBDocumentChunk.id).label('total_chunks')
        ).group_by(DBDocumentChunk.document_id).all()
        
        chunk_counts = {c.document_id: c.total_chunks for c in counts}
        
    except Exception as e:
        print(f"⚠️ Error fetching documents from DB: {e}")
    
    docs = []
    if os.path.exists(source_dir):
        for root, _, files in os.walk(source_dir):
            for filename in sorted(files):
                if filename.endswith(('.txt', '.pdf', '.docx', '.md')):
                    filepath = os.path.join(root, filename)
                    stat = os.stat(filepath)
                    
                    # Sync with DB if missing
                    if filename not in db_docs:
                        from api.models import Domain
                        first_domain = db.query(Domain).first()
                        domain_id = first_domain.id if first_domain else None
                        
                        new_doc = DBDocument(
                            title=filename,
                            source=filename,
                            scope="internal",
                            access_level="employee",
                            version="1.0",
                            domain_id=domain_id
                        )
                        db.add(new_doc); db.commit(); db.refresh(new_doc)
                        db_docs[filename] = new_doc
                    
                    db_doc = db_docs[filename]
                    docs.append({
                        "id": db_doc.id,
                        "title": db_doc.title,
                        "name": filename,
                        "size": f"{stat.st_size} bytes",
                        "type": filename.split('.')[-1].upper(),
                        "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "scope": db_doc.scope or "internal",
                        "access_level": db_doc.access_level or "employee",
                        "chunk_count": chunk_counts.get(db_doc.id, 0),
                        "vector_count": chunk_counts.get(db_doc.id, 0),  # 1 vector per chunk
                        "version": db_doc.version or "1.0"
                    })
    return {"data": docs, "total": len(docs)}

@router.put("/documents/{doc_id}")
async def update_admin_document(doc_id: str, update: DocumentUpdate, req: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != "admin": raise HTTPException(status_code=403, detail="Admin access required")
    
    db_doc = None
    try:
        did = int(doc_id)
        db_doc = db.query(DBDocument).filter(DBDocument.id == did).first()
    except ValueError:
        # doc_id is filename
        db_doc = db.query(DBDocument).filter(DBDocument.source == doc_id).first()
        
    if not db_doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    if update.title is not None: db_doc.title = update.title
    if update.scope is not None: db_doc.scope = update.scope
    if update.access_level is not None: db_doc.access_level = update.access_level
    
    db.commit(); db.refresh(db_doc)
    return {"status": "updated", "data": {
        "id": db_doc.id,
        "title": db_doc.title,
        "scope": db_doc.scope,
        "access_level": db_doc.access_level
    }}

@router.post("/documents/reindex")
async def reindex_all_documents(req: Request, user: User = Depends(get_current_user)):
    if user.role != "admin": raise HTTPException(status_code=403, detail="Admin access required")
    kb = getattr(req.app.state, 'knowledge_base', None)
    if kb and hasattr(kb, '_refresh_documents'):
        kb._refresh_documents()
    kb_docs_len = len(kb.documents) if kb and hasattr(kb, 'documents') else 0
    return {"status": "reindexed", "count": kb_docs_len}

@router.post("/documents/{doc_id}/reindex")
async def reindex_single_document(doc_id: str, req: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != "admin": raise HTTPException(status_code=403, detail="Admin access required")
    
    # 1. Fetch DBDocument
    db_doc = db.query(DBDocument).filter(DBDocument.id == int(doc_id)).first()
    if not db_doc:
        raise HTTPException(status_code=404, detail="Document not found in database")

    # 2. Run indexing in service layer
    source_dir = req.app.state.admin_config["source_directory"]
    try:
        chunks_created = reindex_document(db=db, db_doc=db_doc, source_dir=source_dir)
    except DocumentFileNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except (DocumentExtractionError, DocumentChunkingError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:  # pragma: no cover - defensive logging
        print(f"❌ Error during reindexing chunks: {exc}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(exc))

    # 3. Legacy Refresh
    kb = getattr(req.app.state, 'knowledge_base', None)
    if kb and hasattr(kb, '_refresh_documents'):
        kb._refresh_documents()

    return {"status": "reindexed", "id": doc_id, "chunks_created": chunks_created}

@router.get("/documents/{doc_id}")
async def get_admin_document(doc_id: str, req: Request, user: User = Depends(get_current_user)):
    if user.role != "admin": raise HTTPException(status_code=403, detail="Admin access required")
    source_dir = req.app.state.admin_config["source_directory"]
    
    all_files = []
    if os.path.exists(source_dir):
        for root, _, files in os.walk(source_dir):
            for filename in sorted(files):
                if filename.endswith(('.txt', '.pdf', '.docx', '.md')):
                    all_files.append(os.path.join(root, filename))
    
    target_file = None
    try:
        idx = int(doc_id) - 1
        if 0 <= idx < len(all_files):
            target_file = all_files[idx]
    except ValueError:
        for f in all_files:
            if os.path.basename(f) == doc_id:
                target_file = f
                break
                
    if not target_file or not os.path.exists(target_file):
        raise HTTPException(status_code=404, detail="Document not found")
        
    stat = os.stat(target_file)
    filename = os.path.basename(target_file)
    return {
        "id": doc_id,
        "title": filename,
        "name": filename,
        "size": f"{stat.st_size} bytes",
        "type": filename.split('.')[-1].upper(),
        "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "scope": "internal",
        "access_level": "employee"
    }

@router.get("/knowledge/graph")
async def get_knowledge_graph(req: Request, user: User = Depends(get_current_user)):
    if user.role != "admin": raise HTTPException(status_code=403, detail="Admin access required")
    
    pipeline = getattr(req.app.state, 'pipeline', None)
    if not pipeline or not hasattr(pipeline, 'expert_agent'):
         # Fallback to local parsing if pipeline not fully initialized
         ontology_path = os.path.abspath(os.path.join(os.getcwd(), 'knowledge_base', 'ontology.ttl'))
         if getattr(req.app.state, 'admin_config', {}).get("ontology_path"):
             ontology_path = req.app.state.admin_config["ontology_path"]
         elif not os.path.exists(ontology_path):
             ontology_path = os.path.abspath(os.path.join(os.getcwd(), '..', 'knowledge_base', 'ontology.ttl'))
             
         nodes = []
         links = []
         
         if os.path.exists(ontology_path):
             try:
                 import rdflib
                 g = rdflib.Graph()
                 g.parse(ontology_path, format="turtle")
                 
                 node_set = set()
                 
                 for s, p, o in g:
                     s_str = str(s).split('/')[-1].replace('_', ' ')
                     p_str = str(p).split('/')[-1].replace('_', ' ')
                     o_str = str(o).split('/')[-1].replace('_', ' ')
                     
                     if s_str not in node_set:
                         nodes.append({"id": s_str, "label": s_str})
                         node_set.add(s_str)
                     if o_str not in node_set:
                         nodes.append({"id": o_str, "label": o_str})
                         node_set.add(o_str)
                         
                     links.append({
                         "source": s_str,
                         "target": o_str,
                         "label": p_str,
                         "verified": True
                     })
             except Exception as e:
                 print(f"⚠️ Error parsing ontology: {e}")
                 
         return {"nodes": nodes, "links": links}

    # Use ExpertAgent to export formal triples (supports 'verified' status)
    raw_triples = pipeline.expert_agent.get_all_triples()
    
    nodes = []
    links = []
    node_set = set()

    import hashlib
    def get_node_color(label: str) -> str:
        color_palette = [
            "#3b82f6", # blue-500
            "#10b981", # emerald-500
            "#8b5cf6", # violet-500
            "#f59e0b", # amber-500
            "#ef4444", # red-500
            "#ec4899", # pink-500
            "#14b8a6", # teal-500
        ]
        hash_val = int(hashlib.md5(label.encode('utf-8')).hexdigest(), 16)
        return color_palette[hash_val % len(color_palette)]

    for t in raw_triples:
        s, p, o = t["subject"], t["predicate"], t["object"]
        
        if s not in node_set:
            nodes.append({"id": s, "label": s, "color": get_node_color(s)})
            node_set.add(s)
        if o not in node_set:
            nodes.append({"id": o, "label": o, "color": get_node_color(o)})
            node_set.add(o)
            
        links.append({
            "source": s,
            "target": o,
            "label": p,
            "verified": t.get("verified", False),
            "subject_uri": t.get("subject_uri"),
            "predicate_uri": t.get("predicate_uri"),
            "object_uri": t.get("object_uri")
        })
        
    return {"nodes": nodes, "links": links}

@router.post("/knowledge/manage")
async def manage_knowledge_triple(request: TripleActionRequest, req: Request, user: User = Depends(get_current_user)):
    if user.role != "admin": raise HTTPException(status_code=403, detail="Admin access required")
    
    pipeline = getattr(req.app.state, 'pipeline', None)
    if not pipeline or not hasattr(pipeline, 'expert_agent'):
        raise HTTPException(status_code=500, detail="Expert Agent not initialized")

    success = pipeline.expert_agent.manage_triple(
        subject=request.subject,
        predicate=request.predicate,
        obj=request.object,
        action=request.action,
        subject_uri=request.subject_uri,
        predicate_uri=request.predicate_uri,
        object_uri=request.object_uri
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=f"Failed to {request.action} triple")
        
    return {"status": "success", "action": request.action}

@router.post("/knowledge/build")
async def build_knowledge_base(background_tasks: BackgroundTasks, req: Request, user: User = Depends(get_current_user)):
    if user.role != "admin": raise HTTPException(status_code=403, detail="Admin access required")
    source_dir = req.app.state.admin_config["source_directory"]
    app_state = req.app.state

    def _run_build():
        try:
            build_ontology(source_dir=source_dir, app_state=app_state)
        except Exception as e:  # pragma: no cover - defensive logging
            print(f"❌ Build Failed: {e}")

    background_tasks.add_task(_run_build)
    return {"status": "build_started", "message": "Ontology build running in background"}

@router.get("/stats")
async def get_admin_stats(req: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != "admin": raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        pipeline = req.app.state.pipeline
        stats = pipeline.audit.get_statistics()
        
        # Count files from source_directory to match the Documents page
        source_dir = req.app.state.admin_config.get("source_directory", "docs")
        doc_count = 0
        if os.path.exists(source_dir):
            for root, _, files in os.walk(source_dir):
                doc_count += sum(1 for f in files if f.endswith(('.txt', '.pdf', '.docx', '.md')))
        
        # Attempt to get counts, handle potential errors
        try:
            from api.models import User as DBUser
            total_users = db.query(DBUser).count()
        except Exception as db_err:
            print(f"⚠️ Error querying user count: {db_err}")
            total_users = 0

        active_rules_count = 0
        try:
            from api.models import Rule as DBRule
            active_rules_count = db.query(DBRule).filter(DBRule.active == True).count()
            rules_count = db.query(DBRule).count()
        except:
            rules_count = 0
            pass

        return {
            "status": "online",
            "total_rules": rules_count,
            "active_rules": active_rules_count,
            "total_documents": doc_count,
            "total_users": total_users,
            "uptime": "99.9%",
            "total_queries": stats.get("total_entries", 0),
            "avg_response_time": f"{stats.get('avg_response_time_ms', 0)}ms",
            "error_rate": f"{stats.get('error_rate_percent', 0)}%",
            "cache_hit_rate": f"{stats.get('cache_hit_rate_percent', 0)}%",
            "security_events": stats.get("security_events", 0)
        }
    except Exception as e:
        print(f"❌ CRITICAL error in get_admin_stats: {e}")
        # Return partial failure response instead of 500
        return {
            "status": "degraded",
            "error_detail": str(e),
            "rules_count": 0,
            "total_rules": 0,
            "total_documents": 0,
            "total_users": 0,
            "uptime": "99.9%",
            "total_queries": 0,
            "security_events": 0
        }

@router.get("/health")
async def get_health_status(user: User = Depends(get_current_user)):
    if user.role != "admin": raise HTTPException(status_code=403, detail="Admin access required")
    return {"data": {"postgres": {"status": "online"}, "redis": {"status": "online"}, "ollama": {"status": "online"}}}

@router.post("/documents/upload")
async def upload_document(
    req: Request,
    file: UploadFile = File(...),
    title: str = Form(""),
    scope: str = Form("internal"),
    access_level: str = Form("employee"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user.role != "admin": raise HTTPException(status_code=403, detail="Admin access required")
    
    source_dir = req.app.state.admin_config.get("source_directory", "docs")
    if not os.path.exists(source_dir):
        os.makedirs(source_dir, exist_ok=True)
    
    # Use the provided title as the filename (keeping original extension)
    safe_filename = file.filename
    if title:
        ext = os.path.splitext(file.filename)[1]
        safe_filename = title if title.endswith(ext) else f"{title}{ext}"
    
    file_path = os.path.join(source_dir, safe_filename)
    
    # Save the physical file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Attempt to sync with DB directly so title/scope/access_level are preserved
    try:
        db_doc = db.query(DBDocument).filter(DBDocument.source == safe_filename).first()
        if not db_doc:
            db_doc = DBDocument(
                title=title or safe_filename,
                source=safe_filename,
                scope=scope,
                access_level=access_level,
                version="1.0"
            )
            db.add(db_doc)
        else:
            db_doc.title = title or db_doc.title
            db_doc.scope = scope
            db_doc.access_level = access_level
        db.commit()
    except Exception as e:
        print(f"⚠️ Error saving document metadata to DB: {e}")
        db.rollback()
    
    # Trigger a refresh of the knowledge base indexing
    kb = getattr(req.app.state, 'knowledge_base', None)
    if kb and hasattr(kb, '_refresh_documents'):
        kb._refresh_documents()
    elif kb and hasattr(kb, 'reload_if_changed'):
        kb.reload_if_changed()
        
    return {
        "status": "success", 
        "filename": safe_filename,
        "path": file_path,
        "scope": scope,
        "access_level": access_level,
        "message": f"Document '{safe_filename}' saved to {source_dir}"
    }

@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str, req: Request, user: User = Depends(get_current_user)):
    if user.role != "admin": raise HTTPException(status_code=403, detail="Admin access required")
    source_dir = req.app.state.admin_config.get("source_directory", "docs")
    
    # doc_id may be a numeric index (from frontend) or a filename (legacy)
    target_path = None
    all_files = []
    if os.path.exists(source_dir):
        for root, _, files in os.walk(source_dir):
            for filename in sorted(files):
                if filename.endswith(('.txt', '.pdf', '.docx', '.md')):
                    all_files.append(os.path.join(root, filename))
    
    # Try numeric index first
    try:
        idx = int(doc_id) - 1
        if 0 <= idx < len(all_files):
            target_path = all_files[idx]
    except ValueError:
        # doc_id is a filename
        for f in all_files:
            if os.path.basename(f) == doc_id:
                target_path = f
                break
    
    if target_path and os.path.exists(target_path):
        fname = os.path.basename(target_path)
        os.remove(target_path)
        kb = getattr(req.app.state, 'knowledge_base', None)
        if kb and hasattr(kb, '_refresh_documents'):
            kb._refresh_documents()
        elif kb and hasattr(kb, 'reload_if_changed'):
            kb.reload_if_changed()
        return {"status": "deleted", "file": fname}
    raise HTTPException(status_code=404, detail="File not found")

@router.post("/documents/scan")
async def scan_documents(req: Request, user: User = Depends(get_current_user)):
    if user.role != "admin": raise HTTPException(status_code=403, detail="Admin access required")
    source_dir = req.app.state.admin_config["source_directory"]
    files_found = []
    if os.path.exists(source_dir):
        for root, _, files in os.walk(source_dir):
            for file in files:
                if file.endswith(('.txt', '.pdf', '.docx', '.md')):
                    files_found.append(os.path.join(root, file))
    return {"status": "scanned", "count": len(files_found), "files": files_found}

@router.post("/config/source-directory")
async def set_source_directory(config: DirectoryConfig, req: Request, user: User = Depends(get_current_user)):
    if user.role != "admin": raise HTTPException(status_code=403, detail="Admin access required")
    if not os.path.exists(config.path):
        os.makedirs(config.path, exist_ok=True)
    req.app.state.admin_config["source_directory"] = config.path
    return {"status": "updated", "path": config.path}

@router.get("/metrics")
async def get_system_metrics(user: User = Depends(get_current_user)):
    if user.role != "admin": raise HTTPException(status_code=403, detail="Admin access required")
    # Mocked or partially calculated metrics for monitoring
    return {
        "data": {
            "queries_per_minute": 12.5,
            "avg_response_time_ms": 245,
            "cache_hit_rate": 0.87,
            "error_rate": 0.001,
            "cpu_usage": 45,
            "memory_usage": 62,
            "database_size_mb": 128.5,
            "cache_memory_mb": 64.2,
            "active_users": 5
        }
    }

@router.get("/rules")
async def get_admin_rules(req: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != "admin": raise HTTPException(status_code=403, detail="Admin access required")
    from api.models import Rule as DBRule, Intent as DBIntent
    rules = db.query(DBRule).all()
    result = []
    for r in rules:
        intent_name = "General"
        if r.intent_id:
            intent_obj = db.query(DBIntent).filter(DBIntent.id == r.intent_id).first()
            if intent_obj: intent_name = intent_obj.name
        result.append({
            "id": str(r.id),
            "name": r.name,
            "description": r.description,
            "intent": intent_name,
            "condition": r.condition,
            "action": r.action,
            "priority": r.priority,
            "active": r.active,
            "version": r.version,
            "test_query": r.test_query,
            "trigger_keywords": r.trigger_keywords or []
        })
    return result

@router.post("/rules")
async def create_rule(rule: RuleCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != "admin": raise HTTPException(status_code=403, detail="Admin access required")
    from api.models import Rule as DBRule, Intent as DBIntent
    
    intent_obj = db.query(DBIntent).filter(DBIntent.name == rule.intent).first()
    intent_id = intent_obj.id if intent_obj else None
    domain_id = intent_obj.domain_id if intent_obj else None
    
    # Action can be a message string or a dict of constraints
    action_dict = {"message": rule.action} if isinstance(rule.action, str) else rule.action
    
    new_rule = DBRule(
        domain_id=domain_id,
        name=rule.name,
        description=rule.description or f"Rule for {rule.intent}",
        intent_id=intent_id,
        condition=rule.triggers, # condition field in DB maps to 'triggers' list
        action=action_dict,
        priority=rule.priority,
        required_roles=rule.required_roles,
        test_query=rule.test_query,
        trigger_keywords=rule.trigger_keywords,
        active=True
    )
    db.add(new_rule)
    db.commit()
    db.refresh(new_rule)
    return {"status": "created", "id": new_rule.id, "name": new_rule.name}

@router.patch("/rules/{rule_id}/status")
async def toggle_rule_status(rule_id: str, status: RuleStatusUpdate, req: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != "admin": raise HTTPException(status_code=403, detail="Admin access required")
    from api.models import Rule as DBRule
    try:
        rid = int(rule_id)
        rule = db.query(DBRule).filter(DBRule.id == rid).first()
    except ValueError:
        rule = db.query(DBRule).filter(DBRule.name == rule_id).first()
        
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
        
    rule.active = status.active
    db.commit()
    return {"status": "updated", "id": rule_id, "active": status.active}

@router.post("/rules/{rule_id}/test")
async def test_rule(rule_id: str, test_req: RuleTestRequest, req: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != "admin": raise HTTPException(status_code=403, detail="Admin access required")
    from api.models import Rule as DBRule
    try:
        rid = int(rule_id)
        target_rule = db.query(DBRule).filter(DBRule.id == rid).first()
    except ValueError:
        target_rule = db.query(DBRule).filter(DBRule.name == rule_id).first()
            
    if not target_rule:
        raise HTTPException(status_code=404, detail="Rule not found")
        
    pipeline = getattr(req.app.state, 'pipeline', None)
    if not pipeline:
        raise HTTPException(status_code=500, detail="Pipeline not initialized")
        
    nlp_analysis = pipeline.nlp_core.analyze(test_req.query)
    arbitration = pipeline.arbitrator.arbitrate(nlp_analysis)
    intent = arbitration.final_intent
    
    # Run full pipeline process to get the real chatbot response
    from api.auth import User, UserRole
    import uuid
    
    pseudo_user = User(id="test-user", username="tester", role=UserRole(test_req.user_role))
    
    full_response = pipeline.process(
        question=test_req.query,
        user=pseudo_user,
    )
    
    # Existing simulation logic for firing feedback
    from agents.expert_agent import ProductionRule
    p_rule = ProductionRule(
        id=str(target_rule.id),
        condition=target_rule.condition or [],
        action=target_rule.action or {},
        priority=target_rule.priority,
        description=target_rule.description or "",
        excludes=[],
        required_roles=target_rule.required_roles or [],
        active=target_rule.active,
        test_query=target_rule.test_query,
        trigger_keywords=target_rule.trigger_keywords or []
    )
    
    would_fire = p_rule.check_condition(intent, pseudo_user, nlp_analysis)
    
    # Determine reason for UI feedback
    if would_fire:
        reason = "Rule conditions met (Intent or Keyword match)"
    elif not target_rule.active:
        reason = "Rule is currently inactive"
    elif target_rule.required_roles and test_req.user_role not in target_rule.required_roles:
        reason = f"Role '{test_req.user_role}' does not satisfy required roles"
    else:
        reason = f"Detected intent '{intent}' and query keywords did not trigger this rule"
        
    documents_filtered = p_rule.get_action() if would_fire else {}
        
    return {
        "rule_id": rule_id,
        "query_intent": intent,
        "would_fire": would_fire,
        "reason": reason,
        "action": target_rule.action or {},
        "documents_filtered": {"required": documents_filtered.get("required_docs", []), "forbidden": documents_filtered.get("forbidden_docs", [])},
        "actual_answer": full_response.answer,
        "pipeline_trace": full_response.reasoning
    }

@router.post("/rules/simulate")
async def simulate_rule(sim_req: RuleCreateRequest, test_query: str, test_role: str, req: Request, user: User = Depends(get_current_user)):
    """Simulate a rule definition without saving it to the database"""
    if user.role != "admin": raise HTTPException(status_code=403, detail="Admin access required")
    
    pipeline = getattr(req.app.state, 'pipeline', None)
    if not pipeline:
        raise HTTPException(status_code=500, detail="Pipeline not initialized")
        
    nlp_analysis = pipeline.nlp_core.analyze(test_query)
    arbitration = pipeline.arbitrator.arbitrate(nlp_analysis)
    intent = arbitration.final_intent
    
    would_fire = True
    reason = "Simulated rule conditions met"
    
    # Check triggers
    if sim_req.triggers and intent not in sim_req.triggers:
        would_fire = False
        reason = f"Intent '{intent}' does not match triggers {sim_req.triggers}"
    elif sim_req.required_roles and test_role not in sim_req.required_roles:
        would_fire = False
        reason = f"Role '{test_role}' not in required roles {sim_req.required_roles}"
        
    return {
        "query_intent": intent,
        "would_fire": would_fire,
        "reason": reason,
        "simulated_action": sim_req.action
    }

@router.delete("/rules/{rule_id}")
async def delete_rule(rule_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != "admin": raise HTTPException(status_code=403, detail="Admin access required")
    from api.models import Rule as DBRule
    try:
        rid = int(rule_id)
        rule = db.query(DBRule).filter(DBRule.id == rid).first()
    except ValueError:
        rule = db.query(DBRule).filter(DBRule.name == rule_id).first()
        
    if rule:
        db.delete(rule)
        db.commit()
    return {"status": "deleted", "id": rule_id}

@router.post("/simulate")
async def simulate_rule_impact(req: SimulationRequest, user: User = Depends(get_current_user)):
    if user.role != "admin": raise HTTPException(status_code=403, detail="Admin access required")
    return {"decision": "ALLOWED", "reason": "Simulation mode: No blocking rules found for " + req.user_role, "trace": [{"step": "Authentication", "status": "PASS", "details": f"Role: {req.user_role}"}, {"step": "Intent Recognition", "status": "INFO", "details": f"Intent: {req.intent_override or 'General'}"}, {"step": "Rule Evaluation", "status": "PASS", "details": "No blocking rules"}]}

@router.get("/logs")
@router.get("/audit/logs")
async def get_admin_logs(req: Request, user: User = Depends(get_current_user)):
    if user.role != "admin": raise HTTPException(status_code=403, detail="Admin access required")
    logs = req.app.state.pipeline.audit.query_logs(limit=50)
    
    formatted_logs = []
    for l in logs:
        # Align with AuditLog interface in frontend
        formatted_logs.append({
            "id": l.get("log_id"),
            "trace_id": l.get("trace_id"),
            "timestamp": l.get("timestamp"),
            "user_id": l.get("user", {}).get("user_id"),
            "username": l.get("user", {}).get("username"),
            "user_role": l.get("user", {}).get("role"),
            "query": l.get("query", {}).get("text"),
            "intent": l.get("query", {}).get("intent"),
            "decision": l.get("decision", {}).get("action"),
            "documents_accessed": l.get("decision", {}).get("documents_accessed", []),
            "security_check": l.get("security") or {"allowed": False, "risk_level": "blocked"},
            "performance": l.get("performance") or {"total_time_ms": 0}
        })
        
    return {
        "status": "success",
        "data": {
            "items": formatted_logs,
            "total": len(formatted_logs)
        }
    }

@router.post("/audit/export")
async def export_admin_logs(user: User = Depends(get_current_user)):
    if user.role != "admin": raise HTTPException(status_code=403, detail="Admin access required")
    return {"status": "success", "message": "Export functionality would stream a CSV/JSON file here."}

@router.get("/intents")
async def get_admin_intents(req: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != "admin": raise HTTPException(status_code=403, detail="Admin access required")
    
    # 1. Get intents from database
    db_intents = db.query(DBIntent).all()
    
    # 2. Get patterns from NLP core for discovery
    patterns = req.app.state.pipeline.nlp_core.intent_patterns
    
    results = []
    db_names = {i.name for i in db_intents}
    
    for di in db_intents:
        results.append({
            "id": di.id,
            "name": di.name,
            "description": di.description,
            "risk_level": di.risk_level,
            "requires_approval": di.requires_approval,
            "audit_level": di.audit_level,
            "priority": getattr(di, "priority", 5),
            "metadata": {"source": "database"}
        })
        
    # Discover intents in code but not in DB
    for name in patterns.keys():
        if name not in db_names:
            results.append({
                "id": None,
                "name": name,
                "description": f"Auto-detected domain intent: {name}",
                "risk_level": "medium",
                "requires_approval": False,
                "audit_level": "standard",
                "priority": 5,
                "metadata": {"source": "nlp_patterns"}
            })
            
    return results

@router.put("/intents/{intent_name_or_id}")
async def update_intent(intent_name_or_id: str, update: IntentUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != "admin": raise HTTPException(status_code=403, detail="Admin access required")
    
    db_intent = None
    if intent_name_or_id.isdigit():
        db_intent = db.query(DBIntent).filter(DBIntent.id == int(intent_name_or_id)).first()
    
    if not db_intent:
        db_intent = db.query(DBIntent).filter(DBIntent.name == intent_name_or_id).first()
        
    if not db_intent:
        raise HTTPException(status_code=404, detail=f"Intent '{intent_name_or_id}' not found")
        
    if update.risk_level:
        if update.risk_level not in ['low', 'medium', 'high', 'critical']:
            raise HTTPException(status_code=400, detail="Invalid risk level")
        db_intent.risk_level = update.risk_level
        
    if update.description is not None:
        db_intent.description = update.description
    if update.requires_approval is not None:
        db_intent.requires_approval = update.requires_approval
    if update.audit_level is not None:
        db_intent.audit_level = update.audit_level
    if update.confidence_threshold is not None:
        db_intent.confidence_threshold = update.confidence_threshold
    if update.priority is not None:
        db_intent.priority = update.priority
        
    db.commit()
    return {"status": "updated", "intent": db_intent.name}

@router.put("/rules/{rule_id}")
async def update_rule(rule_id: str, rule_update: RuleCreateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != "admin": raise HTTPException(status_code=403, detail="Admin access required")
    from api.models import Rule as DBRule, Intent as DBIntent
    
    try:
        rid = int(rule_id)
        db_rule = db.query(DBRule).filter(DBRule.id == rid).first()
    except ValueError:
        db_rule = db.query(DBRule).filter(DBRule.name == rule_id).first()
        
    if not db_rule:
        raise HTTPException(status_code=404, detail="Rule not found")
        
    intent_obj = db.query(DBIntent).filter(DBIntent.name == rule_update.intent).first()
    if intent_obj:
        db_rule.intent_id = intent_obj.id
        db_rule.domain_id = intent_obj.domain_id
    
    db_rule.name = rule_update.name
    db_rule.description = rule_update.description or db_rule.description
    db_rule.condition = rule_update.triggers # Map triggers to condition
    db_rule.action = {"message": rule_update.action} if isinstance(rule_update.action, str) else rule_update.action
    db_rule.priority = rule_update.priority
    db_rule.required_roles = rule_update.required_roles
    db_rule.test_query = rule_update.test_query
    db_rule.trigger_keywords = rule_update.trigger_keywords
    
    db.commit()
    return {"status": "updated", "id": db_rule.id, "name": db_rule.name}


# ---------------------------------------------------------------------------
# Settings endpoints
# ---------------------------------------------------------------------------

# Default values used when the DB has no entry for a key yet
_DEFAULT_SETTINGS = {
    "maintenance_mode": {
        "value": False,
        "description": "Route all non-admin traffic to the system status page.",
    },
    "enhanced_audit_logging": {
        "value": True,
        "description": "Persist full reasoning chains and vector attention maps.",
    },
    "source_directory": {
        "value": "docs",
        "description": "Directory scanned by the knowledge-sync watcher.",
    },
    "max_chunk_size": {
        "value": 600,
        "description": "Maximum character length of a document chunk.",
    },
    "chunk_overlap": {
        "value": 100,
        "description": "Overlap in characters between adjacent chunks.",
    },
}


class SettingsUpdateRequest(BaseModel):
    maintenance_mode: Optional[bool] = None
    enhanced_audit_logging: Optional[bool] = None
    source_directory: Optional[str] = None
    max_chunk_size: Optional[int] = None
    chunk_overlap: Optional[int] = None


def _load_settings(db: Session) -> dict:
    """Read all settings from DB, filling in defaults where missing."""
    from api.models import SystemConfig
    rows = {r.key: r.value for r in db.query(SystemConfig).all()}
    result = {}
    for key, meta in _DEFAULT_SETTINGS.items():
        result[key] = rows.get(key, meta["value"])
    return result


def _upsert_setting(db: Session, key: str, value, updated_by: str):
    from api.models import SystemConfig
    row = db.query(SystemConfig).filter(SystemConfig.key == key).first()
    if row:
        row.value = value
        row.updated_by = updated_by
        row.updated_at = datetime.utcnow()
    else:
        row = SystemConfig(
            key=key,
            value=value,
            description=_DEFAULT_SETTINGS.get(key, {}).get("description", ""),
            updated_by=updated_by,
        )
        db.add(row)


@router.get("/settings")
async def get_settings(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    settings = _load_settings(db)
    return {"data": settings}


@router.put("/settings")
async def update_settings(
    payload: SettingsUpdateRequest,
    req: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    updated_keys = []
    for key, value in payload.dict(exclude_none=True).items():
        _upsert_setting(db, key, value, updated_by=user.username)
        updated_keys.append(key)

    db.commit()

    # Apply runtime effects immediately where possible
    if "source_directory" in updated_keys:
        new_dir = payload.source_directory
        if not os.path.exists(new_dir):
            os.makedirs(new_dir, exist_ok=True)
        req.app.state.admin_config["source_directory"] = new_dir
        
        # Restart file watcher with new directory
        old_watcher = getattr(req.app.state, "watcher", None)
        if hasattr(old_watcher, "stop"):
            try:
                old_watcher.stop()
                old_watcher.join(2.0)
                print(f"🛑 Stopped old watcher for directory switch to {new_dir}")
            except Exception as e:
                print(f"⚠️ Failed to stop old watcher: {e}")
                
        try:
            from services.knowledge_sync import start_knowledge_sync
            req.app.state.watcher = start_knowledge_sync(req.app.state)
            print(f"✅ Started new watcher on {new_dir}")
        except Exception as e:
            print(f"❌ Failed to start new watcher on {new_dir}: {e}")
            
        # Update KnowledgeBase auto_discovery path so searches hit the new directory
        kb = getattr(req.app.state, "knowledge_base", None)
        if kb and hasattr(kb, "auto_discovery") and kb.auto_discovery:
            kb.auto_discovery.base_path = new_dir
            print(f"✅ Updated KnowledgeBase AutoDiscovery base_path to {new_dir}")

    if "maintenance_mode" in updated_keys:
        req.app.state.admin_config["maintenance_mode"] = payload.maintenance_mode

    if "enhanced_audit_logging" in updated_keys:
        pipeline = getattr(req.app.state, "pipeline", None)
        if pipeline and hasattr(pipeline, "audit"):
            pipeline.audit.enhanced_logging = payload.enhanced_audit_logging

    return {
        "status": "updated",
        "updated_keys": updated_keys,
        "data": _load_settings(db),
    }

