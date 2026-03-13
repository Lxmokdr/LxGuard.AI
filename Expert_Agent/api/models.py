"""
SQLAlchemy Models for Expert Agent
Maps the 10-section governance schema to Python objects.
"""
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, Float, ForeignKey, CheckConstraint, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from datetime import datetime
from data.database import Base

from data.database import Base
import uuid

# --- 0. Multitenancy & Domain Control ---

class Tenant(Base):
    __tablename__ = "tenants"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    domains = relationship("Domain", back_populates="tenant")
    users = relationship("User", back_populates="tenant")

class Domain(Base):
    __tablename__ = "domains"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, ForeignKey("tenants.id"))
    name = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="domains")
    intents = relationship("Intent", back_populates="domain")
    rules = relationship("Rule", back_populates="domain")
    documents = relationship("Document", back_populates="domain")
    ontology_entities = relationship("OntologyEntity", back_populates="domain")
    answer_modes = relationship("AnswerMode", back_populates="domain")
    json_schemas = relationship("JsonSchema", back_populates="domain")
    prompt_templates = relationship("PromptTemplate", back_populates="domain")

# 1. Core Identity & Access
class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    tenant_id = Column(String, ForeignKey("tenants.id"))
    username = Column(String, nullable=False)
    email = Column(String)
    password_hash = Column(String)
    role = Column(String, CheckConstraint("role IN ('admin', 'developer', 'guest', 'employee')"), nullable=False)
    domain_id = Column(String, ForeignKey("domains.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    domain = relationship("Domain") # Link to domain for default scoping
    queries = relationship("Query", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)

class Permission(Base):
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)

class RolePermission(Base):
    __tablename__ = "role_permissions"
    
    role_id = Column(Integer, ForeignKey("roles.id"), primary_key=True)
    permission_id = Column(Integer, ForeignKey("permissions.id"), primary_key=True)

# 2. Intent & Ontology Layer
class Intent(Base):
    __tablename__ = "intents"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    domain_id = Column(String, ForeignKey("domains.id"))
    name = Column(String, nullable=False)
    description = Column(Text)
    risk_level = Column(String, CheckConstraint("risk_level IN ('low', 'medium', 'high', 'critical')"), nullable=False)
    requires_approval = Column(Boolean, default=False)
    audit_level = Column(String, default="standard")
    priority = Column(Integer, default=5)
    confidence_threshold = Column(Float, default=0.5)
    structured_output_required = Column(Boolean, default=False)
    json_schema_id = Column(Integer, ForeignKey("json_schemas.id"), nullable=True)
    
    # NLP Patterns (formerly hardcoded)
    keywords = Column(JSONB) # List of keywords
    verbs = Column(JSONB)    # List of verbs
    confidence_boost = Column(Float, default=0.0)
    
    # Relationships
    domain = relationship("Domain", back_populates="intents")
    constraints = relationship("IntentConstraint", foreign_keys="IntentConstraint.intent_id")
    rules = relationship("Rule", back_populates="intent")

class OntologyEntity(Base):
    __tablename__ = "ontology_entities"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    domain_id = Column(String, ForeignKey("domains.id"))
    name = Column(String, nullable=False)
    parent_id = Column(Integer, ForeignKey("ontology_entities.id"))
    requires = Column(JSONB) # List of names
    excludes = Column(JSONB) # List of names
    priority = Column(Integer, default=5)
    specificity = Column(String, default="medium")
    
    # Relationships
    domain = relationship("Domain", back_populates="ontology_entities")

class IntentConstraint(Base):
    __tablename__ = "intent_constraints"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    intent_id = Column(Integer, ForeignKey("intents.id"))
    constraint_type = Column(String, CheckConstraint("constraint_type IN ('mutual_exclusion', 'prerequisite')"), nullable=False)
    target_intent_id = Column(Integer, ForeignKey("intents.id"))

# 3. Expert Rules Engine
class Rule(Base):
    __tablename__ = "rules"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    domain_id = Column(String, ForeignKey("domains.id"))
    name = Column(String, nullable=False)
    description = Column(Text)
    intent_id = Column(Integer, ForeignKey("intents.id"))
    condition = Column(JSONB) # trigger_conditions
    action = Column(JSONB)    # {required_docs, forbidden_docs, topic, etc.}
    required_roles = Column(JSONB)
    priority = Column(Integer, default=5)
    version = Column(String, default="1.0")
    active = Column(Boolean, default=True)
    test_query = Column(Text) # Test query for validation
    trigger_keywords = Column(JSONB) # Keywords for easy flagging
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    domain = relationship("Domain", back_populates="rules")
    intent = relationship("Intent", back_populates="rules")
    versions = relationship("RuleVersion", back_populates="rule", cascade="all, delete-orphan")
    history = relationship("RuleExecutionHistory", back_populates="rule", cascade="all, delete-orphan")

class RuleVersion(Base):
    __tablename__ = "rule_versions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    rule_id = Column(Integer, ForeignKey("rules.id"))
    version = Column(String, nullable=False)
    rule_snapshot = Column(JSONB, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    rule = relationship("Rule", back_populates="versions")

class RuleExecutionHistory(Base):
    __tablename__ = "rule_execution_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    domain_id = Column(String, ForeignKey("domains.id"))
    tenant_id = Column(String, ForeignKey("tenants.id"))
    rule_id = Column(Integer, ForeignKey("rules.id"))
    query_id = Column(String)
    fired = Column(Boolean, default=True)
    outcome = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    rule = relationship("Rule", back_populates="history")

# 4. Knowledge Base & Documents
class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    domain_id = Column(String, ForeignKey("domains.id"))
    title = Column(String, nullable=False)
    source = Column(String, nullable=False)
    version = Column(String)
    scope = Column(String, CheckConstraint("scope IN ('internal', 'public', 'restricted')"))
    access_level = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    domain = relationship("Domain", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document")

class DocumentVersion(Base):
    __tablename__ = "document_versions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    version = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    change_summary = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String, ForeignKey("users.id"))

class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    domain_id = Column(String, ForeignKey("domains.id"))
    content = Column(Text, nullable=False)
    embedding = Column(Vector(384))  # pgvector support: all-MiniLM-L6-v2 uses 384 dims
    chunk_index = Column(Integer)
    
    # Relationships
    document = relationship("Document", back_populates="chunks")
    retrieval_events = relationship("RetrievalEvent", back_populates="chunk")

# 5. User Sessions & Access Control
class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"))
    tenant_id = Column(String, ForeignKey("tenants.id"))
    domain_id = Column(String, ForeignKey("domains.id"))
    device_info = Column(Text)
    ip_address = Column(String)
    login_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    is_revoked = Column(Boolean, default=False)

class ApiRateLimit(Base):
    __tablename__ = "api_rate_limits"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"))
    tenant_id = Column(String, ForeignKey("tenants.id"))
    role = Column(String)
    monthly_token_quota = Column(Integer)
    daily_request_limit = Column(Integer)
    current_month_tokens = Column(Integer, default=0)
    current_day_requests = Column(Integer, default=0)
    last_reset = Column(DateTime, default=datetime.utcnow)

# 6. Retrieval & Evidence Tracking
class RetrievalEvent(Base):
    __tablename__ = "retrieval_events"
    
    id = Column(String, primary_key=True)  # UUID
    query_id = Column(String)
    domain_id = Column(String, ForeignKey("domains.id"))
    tenant_id = Column(String, ForeignKey("tenants.id"))
    chunk_id = Column(Integer, ForeignKey("document_chunks.id"))
    relevance_score = Column(Float)
    allowed = Column(Boolean, default=True)
    exclusion_reason = Column(Text)
    
    # Relationships
    chunk = relationship("DocumentChunk", back_populates="retrieval_events")

# 7. Answer Planning & Generation Control
class AnswerPlan(Base):
    __tablename__ = "answer_plans"
    
    id = Column(String, primary_key=True)  # UUID
    domain_id = Column(String, ForeignKey("domains.id"))
    tenant_id = Column(String, ForeignKey("tenants.id"))
    intent_id = Column(Integer, ForeignKey("intents.id"))
    goal = Column(Text)
    steps = Column(JSONB)
    excluded_topics = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)

class GeneratedAnswer(Base):
    __tablename__ = "generated_answers"
    
    id = Column(String, primary_key=True)  # UUID
    query_id = Column(String)
    domain_id = Column(String, ForeignKey("domains.id"))
    tenant_id = Column(String, ForeignKey("tenants.id"))
    answer_text = Column(Text)
    confidence = Column(Float)
    valid = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    validation_reports = relationship("ValidationReport", back_populates="answer")

class ModelUsageMetric(Base):
    __tablename__ = "model_usage_metrics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    query_id = Column(String, ForeignKey("queries.id"))
    domain_id = Column(String, ForeignKey("domains.id"))
    tenant_id = Column(String, ForeignKey("tenants.id"))
    model_name = Column(String, nullable=False)
    prompt_tokens = Column(Integer)
    completion_tokens = Column(Integer)
    total_tokens = Column(Integer)
    inference_time_ms = Column(Integer)
    cost = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

# 8. Validation & Self-Critique
class ValidationReport(Base):
    __tablename__ = "validation_reports"
    
    id = Column(String, primary_key=True)  # UUID
    answer_id = Column(String, ForeignKey("generated_answers.id"))
    validation_score = Column(Float)
    issues = Column(JSONB)
    action_taken = Column(String, CheckConstraint("action_taken IN ('approved', 'regenerated', 'rejected')"))
    
    # Relationships
    answer = relationship("GeneratedAnswer", back_populates="validation_reports")

# 9. Reasoning Trace & Explainability
class Query(Base):
    __tablename__ = "queries"
    
    id = Column(String, primary_key=True)  # UUID
    user_id = Column(String, ForeignKey("users.id"))
    domain_id = Column(String, ForeignKey("domains.id"))
    tenant_id = Column(String, ForeignKey("tenants.id"))
    raw_question = Column(Text, nullable=False)
    detected_language = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="queries")
    reasoning_traces = relationship("ReasoningTrace", back_populates="query")

class ReasoningTrace(Base):
    __tablename__ = "reasoning_traces"
    
    id = Column(String, primary_key=True)  # UUID
    query_id = Column(String, ForeignKey("queries.id"))
    domain_id = Column(String, ForeignKey("domains.id"))
    tenant_id = Column(String, ForeignKey("tenants.id"))
    nlp_output = Column(JSONB)
    intent_arbitration = Column(JSONB)
    rules_triggered = Column(JSONB)
    retrieval_path = Column(JSONB)
    answer_plan = Column(JSONB)
    validation = Column(JSONB)
    
    # Relationships
    query = relationship("Query", back_populates="reasoning_traces")

# 10. Audit & Compliance
class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True)  # UUID
    user_id = Column(String, ForeignKey("users.id"))
    domain_id = Column(String, ForeignKey("domains.id"))
    tenant_id = Column(String, ForeignKey("tenants.id"))
    action = Column(String, nullable=False)
    target = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    meta_info = Column(JSONB)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")

class SecurityEvent(Base):
    __tablename__ = "security_events"
    
    id = Column(String, primary_key=True)  # UUID
    event_type = Column(String, nullable=False)
    user_id = Column(String, ForeignKey("users.id"))
    domain_id = Column(String, ForeignKey("domains.id"))
    tenant_id = Column(String, ForeignKey("tenants.id"))
    severity = Column(String, CheckConstraint("severity IN ('low', 'medium', 'high', 'critical')"))
    details = Column(JSONB)
    ip_address = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

# 11. System Governance
class SystemSetting(Base):
    __tablename__ = "system_settings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    domain_id = Column(String, ForeignKey("domains.id"))
    key = Column(String, nullable=False)
    value = Column(JSONB)
    updated_at = Column(DateTime, default=datetime.utcnow)

# 12. Modular Configuration Tables (NEW)

class AnswerMode(Base):
    __tablename__ = "answer_modes"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    domain_id = Column(String, ForeignKey("domains.id"))
    name = Column(String, nullable=False) # e.g. HYBRID, LOD, PURE_LLM
    requires_rules = Column(Boolean, default=True)
    requires_retrieval = Column(Boolean, default=True)
    requires_structured_output = Column(Boolean, default=False)
    requires_external_data = Column(Boolean, default=False)
    priority = Column(Integer, default=5)
    
    # Relationships
    domain = relationship("Domain", back_populates="answer_modes")

class JsonSchema(Base):
    __tablename__ = "json_schemas"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    domain_id = Column(String, ForeignKey("domains.id"))
    name = Column(String, nullable=False)
    schema_definition = Column(JSONB, nullable=False)
    version = Column(String, default="1.0")
    
    # Relationships
    domain = relationship("Domain", back_populates="json_schemas")

class PromptTemplate(Base):
    __tablename__ = "prompt_templates"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    domain_id = Column(String, ForeignKey("domains.id"))
    intent_id = Column(Integer, ForeignKey("intents.id"), nullable=True)
    answer_mode_id = Column(Integer, ForeignKey("answer_modes.id"))
    template_body = Column(Text, nullable=False)
    version = Column(String, default="1.0")
    is_active = Column(Boolean, default=True)
    
    # Relationships
    domain = relationship("Domain", back_populates="prompt_templates")


# --- System Configuration (Admin Settings) ---
class SystemConfig(Base):
    """Key-value store for admin-configurable system settings."""
    __tablename__ = "system_config"

    key = Column(String, primary_key=True)          # e.g. "maintenance_mode"
    value = Column(JSONB, nullable=False)            # typed: bool / str / int / dict
    description = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String)                     # username of last editor


# --- License Status (cached from vendor license server) ---
class SystemLicenseStatus(Base):
    """Local cache of the latest license state from the vendor server.
    Prevents downtime when vendor server is temporarily unreachable."""
    __tablename__ = "system_license_status"

    id = Column(Integer, primary_key=True, autoincrement=True)
    license_key = Column(String, nullable=False)
    last_checked = Column(DateTime, default=datetime.utcnow)
    license_valid = Column(Boolean, default=False)
    system_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=True)
    server_signature = Column(Text, nullable=True)   # HMAC from vendor


