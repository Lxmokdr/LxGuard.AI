-- Database Schema for Hybrid NLP-Expert Agent Governance
-- Design principle: The database stores decisions, rules, traces, and governance — never raw model reasoning.
-- Optimized for PostgreSQL / Supabase
CREATE EXTENSION IF NOT EXISTS vector;

-- 1. Core Identity & Access (Security First)
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    username TEXT NOT NULL,
    email TEXT,
    password_hash TEXT,
    role TEXT NOT NULL CHECK(role IN ('admin', 'developer', 'guest', 'employee')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS permissions (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS role_permissions (
    role_id INTEGER REFERENCES roles(id),
    permission_id INTEGER REFERENCES permissions(id),
    PRIMARY KEY (role_id, permission_id)
);

-- 2. Intent & Ontology Layer (Critical IP)
CREATE TABLE IF NOT EXISTS intents (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    parent_intent_id INTEGER REFERENCES intents(id),
    risk_level TEXT NOT NULL CHECK(risk_level IN ('low', 'medium', 'high', 'critical')),
    description TEXT
);

CREATE TABLE IF NOT EXISTS intent_constraints (
    id SERIAL PRIMARY KEY,
    intent_id INTEGER REFERENCES intents(id),
    constraint_type TEXT NOT NULL CHECK(constraint_type IN ('mutual_exclusion', 'prerequisite')),
    target_intent_id INTEGER REFERENCES intents(id)
);

-- 3. Expert Rules Engine (Deterministic Core)
CREATE TABLE IF NOT EXISTS rules (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    intent_id INTEGER REFERENCES intents(id),
    condition JSONB, -- IF clause
    action JSONB,    -- THEN clause
    priority INTEGER DEFAULT 5,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS rule_versions (
    id SERIAL PRIMARY KEY,
    rule_id INTEGER REFERENCES rules(id),
    version TEXT NOT NULL,
    rule_snapshot JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS rule_execution_history (
    id SERIAL PRIMARY KEY,
    rule_id INTEGER REFERENCES rules(id),
    query_id TEXT,
    fired BOOLEAN DEFAULT TRUE,
    outcome TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Knowledge Base & Documents
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    source TEXT NOT NULL,
    version TEXT,
    scope TEXT CHECK(scope IN ('internal', 'public', 'restricted')),
    access_level TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS document_versions (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id),
    version TEXT NOT NULL,
    content TEXT NOT NULL,
    change_summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    domain_id TEXT REFERENCES domains(id) ON DELETE SET NULL,
    content TEXT NOT NULL,
    embedding VECTOR(384),
    chunk_index INTEGER
);

-- 5. User Sessions & Access Control
CREATE TABLE IF NOT EXISTS user_sessions (
    id TEXT PRIMARY KEY, -- UUID
    user_id TEXT REFERENCES users(id),
    device_info TEXT,
    ip_address TEXT,
    login_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_revoked BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS api_rate_limits (
    id SERIAL PRIMARY KEY,
    user_id TEXT REFERENCES users(id),
    role TEXT,
    monthly_token_quota BIGINT,
    daily_request_limit INTEGER,
    current_month_tokens BIGINT DEFAULT 0,
    current_day_requests INTEGER DEFAULT 0,
    last_reset TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Retrieval & Evidence Tracking
CREATE TABLE IF NOT EXISTS retrieval_events (
    id TEXT PRIMARY KEY, -- UUID
    query_id TEXT,
    chunk_id INTEGER REFERENCES document_chunks(id),
    relevance_score REAL,
    allowed BOOLEAN DEFAULT TRUE,
    exclusion_reason TEXT
);

-- 7. Answer Planning & Generation Control
CREATE TABLE IF NOT EXISTS answer_plans (
    id TEXT PRIMARY KEY, -- UUID
    intent_id INTEGER REFERENCES intents(id),
    goal TEXT,
    steps JSONB,
    excluded_topics JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS generated_answers (
    id TEXT PRIMARY KEY, -- UUID
    query_id TEXT,
    answer_text TEXT,
    confidence REAL,
    valid BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS model_usage_metrics (
    id SERIAL PRIMARY KEY,
    query_id TEXT REFERENCES queries(id),
    model_name TEXT NOT NULL,
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    total_tokens INTEGER,
    inference_time_ms INTEGER,
    cost REAL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. Validation & Self-Critique
CREATE TABLE IF NOT EXISTS validation_reports (
    id TEXT PRIMARY KEY, -- UUID
    answer_id TEXT REFERENCES generated_answers(id),
    validation_score REAL,
    issues JSONB,
    action_taken TEXT CHECK(action_taken IN ('approved', 'regenerated', 'rejected'))
);

-- 9. Reasoning Trace & Explainability
CREATE TABLE IF NOT EXISTS queries (
    id TEXT PRIMARY KEY, -- UUID
    user_id TEXT REFERENCES users(id),
    raw_question TEXT NOT NULL,
    detected_language TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS reasoning_traces (
    id TEXT PRIMARY KEY, -- UUID
    query_id TEXT REFERENCES queries(id),
    nlp_output JSONB,
    intent_arbitration JSONB,
    rules_triggered JSONB,
    retrieval_path JSONB,
    answer_plan JSONB,
    validation JSONB
);

-- 10. Audit & Compliance
CREATE TABLE IF NOT EXISTS audit_logs (
    id TEXT PRIMARY KEY, -- UUID
    user_id TEXT REFERENCES users(id),
    action TEXT NOT NULL,
    target TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    meta_info JSONB
);

CREATE TABLE IF NOT EXISTS security_events (
    id TEXT PRIMARY KEY, -- UUID
    event_type TEXT NOT NULL, -- 'login_failure', 'unauthorized_access', 'pii_detection'
    user_id TEXT REFERENCES users(id),
    severity TEXT CHECK(severity IN ('low', 'medium', 'high', 'critical')),
    details JSONB,
    ip_address TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 11. System Governance
CREATE TABLE IF NOT EXISTS system_settings (
    id SERIAL PRIMARY KEY,
    key TEXT NOT NULL UNIQUE,
    value JSONB,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Initial Governance Data
INSERT INTO system_settings (key, value) VALUES ('deterministic_mode', 'true') ON CONFLICT (key) DO NOTHING;
INSERT INTO system_settings (key, value) VALUES ('max_tokens', '500') ON CONFLICT (key) DO NOTHING;
INSERT INTO system_settings (key, value) VALUES ('confidence_threshold_high', '0.8') ON CONFLICT (key) DO NOTHING;
INSERT INTO system_settings (key, value) VALUES ('confidence_threshold_medium', '0.6') ON CONFLICT (key) DO NOTHING;

-- Default Admin User
INSERT INTO users (id, username, email, role, is_active) 
VALUES ('admin-0000-0000-0000', 'admin', 'admin@expert-agent.local', 'admin', true) 
ON CONFLICT (id) DO NOTHING;

-- Seed Users
INSERT INTO users (id, username, email, role, is_active) 
VALUES ('dev-0000-0000-0000', 'developer', 'dev@expert-agent.local', 'developer', true) 
ON CONFLICT (id) DO NOTHING;

INSERT INTO users (id, username, email, role, is_active) 
VALUES ('emp-0000-0000-0000', 'employee', 'employee@expert-agent.local', 'employee', true) 
ON CONFLICT (id) DO NOTHING;

INSERT INTO users (id, username, email, role, is_active) 
VALUES ('guest-0000-0000-0000', 'guest', 'guest@expert-agent.local', 'guest', true) 
ON CONFLICT (id) DO NOTHING;
