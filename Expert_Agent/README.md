# Expert Agent — Hybrid NLP Architecture

This directory contains the core logic for the **Hybrid NLP-Expert Agent**, a security-critical AI system designed for enterprise environments. It combines probabilistic NLP (LLMs) with deterministic Expert Rules (Symbolic Logic) across an 8-layer architecture to ensure accuracy, safety, and auditability.

---

## 🏗️ 8-Layer Architecture

| Layer | Name | Component | Responsibility |
|-------|------|-----------|----------------|
| 0 | Security Check | `security/` | RBAC query safety & PII filtering |
| 1 | NLP Core | `core/nlp_core.py` | Semantic parsing and intent hypothesis generation |
| 2 | Expert Brain | `agents/expert_agent.py` | Symbolic validation against formal ontologies |
| 3 | Intent Arbitration | `core/intent_arbitration.py` | Conflict resolution + RBAC + **off-topic guard** |
| 4 | Agent-Driven Retrieval | `engines/retrieval_engine.py` | Two-tier retrieval (Symbolic + Semantic) |
| 5 | Answer Planning | `core/answer_planner.py` | Structured "Answer Contract" creation + validation |
| 6 | Controlled Generation | `utils/explanation.py` | LLM execution following the plan, streamed |
| 7 | Self-Validation | `agents/validation_agent.py` | Fidelity and rule compliance checks |
| 8 | Explainability & Audit | `core/hybrid_pipeline.py` | Full reasoning trace + audit log |

### 🚦 Off-Topic Guard (Layer 3)

When a query is classified as `General` intent, the pipeline exits at Layer 3 and returns a redirect message instead of running the full 8-layer pipeline on unanswerable questions.

---

## 🔄 Answer Modes

The backend supports three distinct modes via `POST /api/chat/stream`:

| Mode (`mode` param) | Path | Description |
|--------------------|------|-------------|
| `full` | Full 8-layer `HybridPipeline` | Project-specific grounded answers |
| `external` | `HybridKnowledgeAgent` (LOD) | DBpedia SPARQL + LLM synthesis |
| `llm` | Direct `OllamaClient` stream | Pure generative response |

---

## 📂 File Breakdown

### 🚀 Core & Orchestration

| File | Responsibility |
| :--- | :--- |
| [api/api_hybrid.py](api/api_hybrid.py) | **Main Entry Point**: FastAPI server + startup initialization |
| [core/hybrid_pipeline.py](core/hybrid_pipeline.py) | **Orchestrator**: 8-layer pipeline, off-topic guard, SSE streaming |
| [api/routers/chat.py](api/routers/chat.py) | **Chat Router**: Mode routing (`full`, `external`, `llm`) + SSE |

### 🧠 Intelligence & Logic (`core/`)

| File | Responsibility |
| :--- | :--- |
| [core/nlp_core.py](core/nlp_core.py) | Layer 1: Probabilistic NER, intent classification, entity extraction |
| [core/intent_arbitration.py](core/intent_arbitration.py) | Layer 3: Ontology-based conflict resolution + off-topic guard |
| [core/answer_planner.py](core/answer_planner.py) | Layer 5: Structured answer contract creation |

### 📚 Agents & Engines

| File | Responsibility |
| :--- | :--- |
| [agents/expert_agent.py](agents/expert_agent.py) | Layer 2: Deterministic ontology + RBAC rule enforcement |
| [agents/hybrid_agent.py](agents/hybrid_agent.py) | LOD/LLM mode orchestration (external & general knowledge fallback) |
| [agents/validation_agent.py](agents/validation_agent.py) | Layer 7: Self-correction and hallucination detection |
| [engines/retrieval_engine.py](engines/retrieval_engine.py) | Layer 4: Symbolic filtering + semantic ranking |
| [engines/lod_client.py](engines/lod_client.py) | DBpedia SPARQL client with multi-step fallback |
| [engines/ollama_client.py](engines/ollama_client.py) | Ollama LLM client (streaming and non-streaming) |
| [utils/explanation.py](utils/explanation.py) | Layer 6: Streaming LLM generation with context grounding |

### ⚙️ Configuration (`config/`)

| File | Responsibility |
| :--- | :--- |
| [config/ontology.yaml](config/ontology.yaml) | Concept hierarchy, priorities, and exclusion rules |
| [config/templates.yaml](config/templates.yaml) | Answer structure templates per intent |

> **Note**: `config/rules.yaml` is a legacy file from an earlier domain. All live rules are stored in the PostgreSQL `rules` table and managed via the Admin Console.

### 📊 Data & Persistence

| File | Responsibility |
| :--- | :--- |
| [data/knowledge_base.py](data/knowledge_base.py) | Static knowledge base with doc metadata and topics |
| [data/database.py](data/database.py) | SQLAlchemy engine and session management |
| [api/models.py](api/models.py) | ORM models for PostgreSQL + pgvector and full governance schema |

### 🧩 Service Layer (`services/`)

| File | Responsibility |
| :--- | :--- |
| [services/document_indexing.py](services/document_indexing.py) | Single-document reindexing: extraction, **paragraph-aware chunking with overlap**, pgvector persistence |
| [services/ontology_service.py](services/ontology_service.py) | Ontology build orchestration |
| [services/knowledge_sync.py](services/knowledge_sync.py) | **Real-Time Sync**: watchdog-based auto-indexing on file creation/modification/deletion |

---

## 📑 Document Chunking

Documents are split using a **paragraph-aware algorithm** with overlap:

```
Empty text  → returns []           (no crash)
Short text  → 1 chunk, no overlap  (covers tiny files like test.txt)
Long text   → paragraph chunks + 100-char overlap between adjacent chunks
```

Controlled by two admin-configurable settings:
- **Max Chunk Size** (default: 600 chars) — maximum length before a paragraph is further split by sentence
- **Chunk Overlap** (default: 100 chars) — trailing context carried into the next chunk

---

## 📁 Knowledge Base (`docs/`)

Markdown files in `../docs/` (mounted at `/app/docs` in Docker) are indexed at startup.

> **Automated Sync**: Drop any `.pdf`, `.md`, `.docx`, or `.txt` file into `docs/` and the background watchdog service indexes it automatically.

---

## 🔐 Security & RBAC

RBAC is enforced at **Layer 0 (Security Check)** and **Layer 3 (Intent Arbitration)**:

- **OIDC Authentication**: Keycloak integration with RS256 JWT validation.
- **RBAC**: Role-based access enforced per intent (e.g., `AML_InternalFraud` requires `admin`).
- **PII Detection**: Automatic redaction using deterministic hashing.
- **Audit Logging**: Full trace of all 8-layer decisions in PostgreSQL. Toggle via Admin Settings.
- **Pipeline Caching**: Redis-backed lookup with governance-aware cache keys.
- **Real-Time Sync**: `watchdog` service keeps knowledge in sync with `docs/`.
- **Off-Topic Guard**: Queries outside project scope are rejected at Layer 3.

---

## 🛠️ Admin Console Features

The admin panel (`http://localhost:3000`) provides:

| Section | Feature |
|---|---|
| **Rules** | Create/edit production rules — Target Intent field supports typing new intent names (CreatableSelect) |
| **Documents** | Upload individual files or pick an entire local folder to bulk-upload |
| **Settings / System** | Toggle Maintenance Mode, Enhanced Audit Logging, configure Source Directory |
| **Settings / Chunking** | Adjust Max Chunk Size and Chunk Overlap (persisted in `system_config` DB table) |

---

## 📊 Database Schema (11 Operational Tables)

| Table | Purpose |
|---|---|
| `users` | RBAC accounts and hashed credentials |
| `user_sessions` | Login/logout tracking |
| `intents` | Concept classification and priority definitions |
| `rules` | IF-THEN-RBAC logic blocks |
| `documents` & `document_chunks` | Knowledge base with pgvector embeddings |
| `retrieval_events` | Source document citations and relevance scores |
| `rule_execution_history` | Deterministic trace of which rules fired |
| `model_usage_metrics` | Token usage and processing time |
| `queries`, `reasoning_traces`, `audit_logs`, `security_events` | Full SIEM audit trail |
| **`system_config`** | **Admin settings key-value store (new)** |

---

## 🚀 Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Configure Environment
Edit `.env`:
```env
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=hybrid_db
OLLAMA_HOST=http://ollama:11434
REDIS_HOST=cache
REDIS_PORT=6379
```

### 3. Start the Backend
```bash
uvicorn api_hybrid:app --host 0.0.0.0 --port 8001 --reload
```

> The `system_config` table is auto-created by SQLAlchemy at startup — no migration needed.

---

## 🐳 Docker Deployment

```bash
# From project root
docker compose up -d --build
```

**Services**:
- `expert-agent-backend` — FastAPI (port 8001)
- `expert-agent-db` — PostgreSQL 15 + pgvector (port 5434)
- `expert-agent-cache` — Redis (port 6379)
- `expert-agent-ollama` — Ollama LLM (port 11435)
- `expert-agent-chatbot` — React chatbot UI (port 5173)
- `expert-agent-admin` — Admin UI (port 3000)

**Volume Mounts**:
- `./Expert_Agent:/app` — Live code (hot reload)
- `./docs:/app/docs` — Knowledge base

---

## 🧪 System Verification

```bash
docker compose exec backend bash -c "python scripts/test_all_apis.py"
```

---

**For API documentation, visit: http://localhost:8001/docs**
