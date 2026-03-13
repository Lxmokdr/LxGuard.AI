"""
Pipeline Contracts - Strict Typed Input/Output for All Layers

Enforces type safety and prevents state mutation across the 8-layer pipeline.
Each layer has explicit input/output contracts using Pydantic models.
"""
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


# ============================================================================
# Enums for Type Safety
# ============================================================================

class IntentType(str, Enum):
    """Valid intent types"""
    INSTALLATION = "Installation"
    ROUTING = "Routing"
    DEPLOYMENT = "Deployment"
    API_REFERENCE = "API_Reference"
    CONFIGURATION = "Configuration"
    TROUBLESHOOTING = "Troubleshooting"
    GENERAL = "General"


class RiskLevel(str, Enum):
    """Risk levels for intents"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class UserRole(str, Enum):
    """User roles for RBAC"""
    ADMIN = "admin"
    EMPLOYEE = "employee"
    DEVELOPER = "developer"
    GUEST = "guest"


# ============================================================================
# Layer 1: NLP Core
# ============================================================================

class NLPInput(BaseModel):
    """Input contract for NLP layer"""
    query: str = Field(..., min_length=1, max_length=5000)
    language: Optional[str] = Field(None, description="Detected or specified language")
    user_id: str = Field(..., description="User ID for cache governance")
    role: UserRole = Field(..., description="User role for RBAC")
    
    class Config:
        frozen = True  # Immutable


class Entity(BaseModel):
    """Named entity extracted from query"""
    text: str
    label: str
    start: int
    end: int


class IntentHypothesis(BaseModel):
    """Intent hypothesis with confidence"""
    intent: IntentType
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str


class NLPOutput(BaseModel):
    """Output contract for NLP layer"""
    entities: List[Entity]
    intent_hypotheses: List[IntentHypothesis]
    detected_language: str
    processing_time_ms: float
    cache_hit: bool = False
    
    class Config:
        frozen = True


# ============================================================================
# Layer 2: Expert Agent
# ============================================================================

class ExpertInput(BaseModel):
    """Input contract for Expert Agent layer"""
    nlp_output: NLPOutput
    user_role: UserRole
    query: str
    
    class Config:
        frozen = True


class RuleMatch(BaseModel):
    """Matched expert rule"""
    rule_id: str
    rule_name: str
    priority: int
    action: Dict[str, Any]


class ExpertOutput(BaseModel):
    """Output contract for Expert Agent layer"""
    validated_intent: IntentType
    risk_level: RiskLevel
    matched_rules: List[RuleMatch]
    constraints: Dict[str, Any]
    processing_time_ms: float
    
    class Config:
        frozen = True


# ============================================================================
# Layer 3: Intent Arbitration & RBAC
# ============================================================================

class ArbitrationInput(BaseModel):
    """Input contract for Arbitration layer"""
    nlp_output: NLPOutput
    expert_output: ExpertOutput
    user_id: str
    user_role: UserRole
    
    class Config:
        frozen = True


class RBACDecision(BaseModel):
    """RBAC access decision"""
    allowed: bool
    reason: Optional[str] = None
    restricted_topics: List[str] = []


class ArbitrationOutput(BaseModel):
    """Output contract for Arbitration layer"""
    final_intent: IntentType
    rbac_decision: RBACDecision
    confidence: float = Field(..., ge=0.0, le=1.0)
    arbitration_reasoning: str
    processing_time_ms: float
    
    class Config:
        frozen = True


# ============================================================================
# Layer 4: Retrieval
# ============================================================================

class RetrievalInput(BaseModel):
    """Input contract for Retrieval layer"""
    query: str
    final_intent: IntentType
    user_role: UserRole
    user_id: str
    rbac_decision: RBACDecision
    top_k: int = Field(5, ge=1, le=20)
    
    class Config:
        frozen = True


class DocumentChunk(BaseModel):
    """Retrieved document chunk"""
    chunk_id: int
    document_id: int
    content: str
    relevance_score: float = Field(..., ge=0.0, le=1.0)
    source: str
    metadata: Dict[str, Any] = {}


class RetrievalOutput(BaseModel):
    """Output contract for Retrieval layer"""
    chunks: List[DocumentChunk]
    total_candidates: int
    filtered_count: int
    cache_hit: bool = False
    processing_time_ms: float
    
    class Config:
        frozen = True


# ============================================================================
# Layer 5: Answer Planning
# ============================================================================

class PlanningInput(BaseModel):
    """Input contract for Planning layer"""
    query: str
    final_intent: IntentType
    retrieval_output: RetrievalOutput
    user_role: UserRole
    
    class Config:
        frozen = True


class AnswerStep(BaseModel):
    """Step in answer plan"""
    step_number: int
    description: str
    evidence_chunk_ids: List[int]


class PlanningOutput(BaseModel):
    """Output contract for Planning layer"""
    goal: str
    steps: List[AnswerStep]
    excluded_topics: List[str]
    required_disclaimers: List[str] = []
    processing_time_ms: float
    
    class Config:
        frozen = True


# ============================================================================
# Layer 6: Generation
# ============================================================================

class GenerationInput(BaseModel):
    """Input contract for Generation layer"""
    query: str
    plan: PlanningOutput
    chunks: List[DocumentChunk]
    language: str
    
    class Config:
        frozen = True


class GenerationOutput(BaseModel):
    """Output contract for Generation layer"""
    answer_text: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    citations: List[int] = []  # chunk_ids
    processing_time_ms: float
    
    class Config:
        frozen = True


# ============================================================================
# Layer 7: Validation
# ============================================================================

class ValidationInput(BaseModel):
    """Input contract for Validation layer"""
    query: str
    answer: GenerationOutput
    plan: PlanningOutput
    chunks: List[DocumentChunk]
    
    class Config:
        frozen = True


class ValidationIssue(BaseModel):
    """Validation issue found"""
    severity: str  # "error", "warning", "info"
    issue_type: str
    description: str


class ValidationOutput(BaseModel):
    """Output contract for Validation layer"""
    valid: bool
    validation_score: float = Field(..., ge=0.0, le=1.0)
    issues: List[ValidationIssue]
    checks_performed: Dict[str, bool]
    processing_time_ms: float
    
    class Config:
        frozen = True


# ============================================================================
# Layer 8: Explainability (Full Trace)
# ============================================================================

class ReasoningTrace(BaseModel):
    """Complete reasoning trace for explainability"""
    query_id: str
    user_id: str
    timestamp: datetime
    nlp_analysis: Dict[str, Any]
    expert_validation: Dict[str, Any]
    intent_arbitration: Dict[str, Any]
    retrieval_path: Dict[str, Any]
    answer_plan: Dict[str, Any]
    generation: Dict[str, Any]
    validation: Dict[str, Any]
    total_processing_time_ms: float
    
    class Config:
        frozen = True


# ============================================================================
# Pipeline Context (Governance State)
# ============================================================================

class PipelineContext(BaseModel):
    """Immutable context passed through entire pipeline"""
    user_id: str
    user_role: UserRole
    rule_version_hash: str = Field(..., description="Hash of active rules for cache governance")
    settings_version_hash: str = Field(..., description="Hash of system settings for cache governance")
    query_id: str
    timestamp: datetime
    
    class Config:
        frozen = True
    
    def get_cache_context(self) -> str:
        """Get cache context string for governance-aware keys"""
        return f"{self.user_id}:{self.user_role.value}:{self.rule_version_hash}:{self.settings_version_hash}"
