/**
 * TypeScript Types for Expert Agent Admin UI
 */

// ============================================================================
// User & Authentication
// ============================================================================

export type UserRole = 'admin' | 'employee' | 'developer' | 'guest';

export interface User {
    id: string;
    username: string;
    email?: string;
    role: UserRole;
    is_active: boolean;
    created_at: string;
}

// ============================================================================
// Rules & Ontology
// ============================================================================

export interface Intent {
    name: string;
    parent?: string;
    description: string;
    risk_level: 'low' | 'medium' | 'high' | 'critical';
    mutually_exclusive: string[];
    prerequisites: {
        system_requirements: string[];
        intent_requirements: string[];
    };
    compatible_with: string[];
    priority: number;
    specificity: 'low' | 'medium' | 'high';
    rbac_default: UserRole[];
    metadata: {
        category: string;
        complexity: string;
        estimated_docs_needed: number;
    };
}

export interface Rule {
    id: string;
    name: string;
    triggers?: string[]; // Intent names
    allowed_roles?: UserRole[];
    action: {
        topic?: string;
        required_docs?: string[];
        forbidden_docs?: string[];
        answer_structure?: string;
    };
    condition?: Record<string, any>;
    priority: number;
    description?: string;
    excludes?: string[];
    active: boolean;
    created_at?: string;
    test_query?: string;
    trigger_keywords?: string[];
}

export interface RuleTestResult {
    rule_id: string;
    would_fire: boolean;
    reason: string;
    documents_filtered: {
        required: string[];
        forbidden: string[];
    };
    action?: {
        message?: string;
        [key: string]: any;
    };
}

// ============================================================================
// Documents
// ============================================================================

export type DocumentScope = 'internal' | 'public' | 'restricted';
export type DocumentAccessLevel = 'admin' | 'employee' | 'all';

export interface Document {
    id: number;
    title: string;
    source: string;
    version?: string;
    scope: DocumentScope;
    access_level?: DocumentAccessLevel;
    created_at: string;
    chunk_count?: number;
    vector_count?: number;
    used_by_rules?: string[];
}

export interface DocumentChunk {
    id: number;
    document_id: number;
    content: string;
    chunk_index: number;
    embedding?: number[];
}

export interface DocumentUploadRequest {
    title: string;
    file: File;
    scope: DocumentScope;
    access_level: DocumentAccessLevel;
    version?: string;
}

// ============================================================================
// Audit Logs
// ============================================================================

export interface AuditLog {
    id: number;
    trace_id: string;
    timestamp: string;
    user_id: string;
    username: string;
    user_role: UserRole;
    query: string;
    intent: string;
    decision: 'approved' | 'rejected' | 'flagged';
    reason?: string;
    documents_accessed: string[];
    confidence?: number;
    security_check: {
        allowed: boolean;
        risk_level: string;
    };
    performance: {
        total_time_ms: number;
        nlp_time_ms?: number;
        retrieval_time_ms?: number;
        generation_time_ms?: number;
    };
}

export interface ReasoningTrace {
    nlp_analysis: {
        intent_hypotheses: Array<{ intent: string; confidence: number; reasoning: string }>;
        entities: Array<{ text: string; label: string }>;
        semantic_roles: any;
        keywords: string[];
        question_type: string;
    };
    intent_arbitration: {
        final_intent: string;
        confidence: number;
        reason: string;
        rejected_intents: string[];
    };
    retrieval_path: {
        tier1_symbolic: any;
        tier2_semantic: any;
        tier3_evidence: any;
        grounding: {
            sufficient: boolean;
            coverage: number;
        };
        final_documents: string[];
    };
    answer_plan: {
        goal: string;
        structure: string;
        steps: Array<{ step_number: number; description: string }>;
        excluded_topics: string[];
        max_length: number;
    };
    documents: Array<{
        name: string;
        score: number;
        sections: string[];
    }>;
}

// ============================================================================
// System Monitoring
// ============================================================================

export interface SystemHealth {
    postgres: ServiceStatus;
    redis: ServiceStatus;
    ollama: ServiceStatus;
    keycloak: ServiceStatus;
}

export interface ServiceStatus {
    status: 'online' | 'offline' | 'degraded';
    latency_ms?: number;
    message?: string;
    details?: any;
}

export interface SystemMetrics {
    timestamp: string;
    queries_per_minute: number;
    avg_response_time_ms: number;
    error_rate: number;
    cache_hit_rate: number;
    database_size_mb: number;
    cache_memory_mb: number;
    active_users: number;
}

export interface MetricsHistory {
    timestamps: string[];
    queries: number[];
    latency: number[];
    errors: number[];
    cache_hits: number[];
}

// ============================================================================
// Cache Management
// ============================================================================

export interface CacheStats {
    total_keys: number;
    memory_used_mb: number;
    hit_rate: number;
    miss_rate: number;
    evictions: number;
    by_type: {
        nlp: number;
        retrieval: number;
        plan: number;
        document: number;
    };
}

// ============================================================================
// Configuration
// ============================================================================

export interface SystemSettings {
    llm_model: string;
    max_query_length: number;
    default_cache_ttl: number;
    max_validation_retries: number;
    enable_embeddings: boolean;
    enable_local_llm: boolean;
    enable_auto_discovery: boolean;
    enable_pii_detection: boolean;
    session_timeout_minutes: number;
}

// ============================================================================
// API Responses
// ============================================================================

export interface ApiResponse<T> {
    success: boolean;
    data?: T;
    error?: string;
    message?: string;
}

export interface PaginatedResponse<T> {
    items: T[];
    total: number;
    page: number;
    page_size: number;
    total_pages: number;
}

// ============================================================================
// Query Simulator
// ============================================================================

export interface QueryTestRequest {
    query: string;
    user_role: UserRole;
    target_language?: string;
}

export interface QueryTestResponse {
    answer: string;
    reasoning: ReasoningTrace;
    validation: {
        valid: boolean;
        score: number;
        checks: Record<string, boolean>;
        issues: string[];
    };
    confidence: number;
    detected_language?: string;
    processing_time_ms: number;
}

// ============================================================================
// Analytics
// ============================================================================

export interface IntentAnalytics {
    intent: string;
    count: number;
    avg_confidence: number;
    success_rate: number;
    avg_response_time_ms: number;
}

export interface DocumentAnalytics {
    document_id: number;
    title: string;
    retrieval_count: number;
    avg_relevance_score: number;
    last_used: string;
}

export interface UserActivity {
    user_id: string;
    username: string;
    query_count: number;
    last_active: string;
    top_intents: string[];
    avg_confidence: number;
}
