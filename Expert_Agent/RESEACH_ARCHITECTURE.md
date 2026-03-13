# Research Paper: Neuro-Symbolic Hybrid NLP-Expert Architecture
## Technical Overview and Operational Workflows

### 1. Abstract
This document outlines the architecture and operational mechanics of the **Hybrid NLP-Expert Agent**, a dual-mode artificial intelligence system designed to combine the probabilistic strengths of Large Language Models (LLMs) with the deterministic reliability of Symbolic Expert Systems. The system implements a novel **8-Layer Neuro-Symbolic Pipeline** to ensure that enterprise-grade queries (e.g., Anti-Fraud and AML monitoring) are governed by formal ontologies while maintaining human-like conversational flexibility.

---

### 2. Core Architecture: The 8-Layer Pipeline
The system processes every incoming query through a serialized pipeline of eight intelligence layers, each responsible for a specific stage of reasoning, verification, or generation.

#### Layer 0: Security & Policy Enforcement
- **Mechanism**: RBAC (Role-Based Access Control) integrated with OIDC (Keycloak).
- **Function**: Queries are intercepted and scanned for PII (Personally Identifiable Information) and policy violations before entering the reasoning engine.

#### Layer 1: Advanced NLP & Semantic Parsing
- **Technology**: spaCy + Transformer-based NER (Named Entity Recognition).
- **Function**: Extracts semantic intents and entities from raw natural language, generating multiple weighted "intent hypotheses."

#### Layer 2: Symbolic Expert Brain
- **Technology**: Production Rule Engine + RDF/OWL-inspired Ontology.
- **Function**: Validates intent hypotheses against a formal "World Model" (Ontology). If an intent violates the logical constraints of the system (e.g., asking for admin-only `AML_InternalFraud` data as a guest), it is flagged immediately.

#### Layer 3: Intent Arbitration & Off-Topic Guard
- **Mechanism**: Conflict resolution algorithm.
- **Function**: Harmonizes the probabilistic output of Layer 1 with the deterministic constraints of Layer 2. It also implements an **Off-Topic Guard** that rejects non-domain queries (e.g., general knowledge) when in high-precision mode.

#### Layer 4: Multi-Tier Agent-Driven Retrieval
- **Tier 1 (Symbolic)**: Filters the document corpus based on metadata, document scope, and expert tags.
- **Tier 2 (Semantic)**: Ranks the filtered subset using Vector Embeddings (pgvector) and cosine similarity.

#### Layer 5: Recursive Answer Planning
- **Function**: Generates an "Answer Contract" specifying exactly which pieces of evidence will be used, what topics are excluded, and the structural skeleton of the final response.

#### Layer 6: Grounded Generation (LLM)
- **Technology**: Local LLM Inference (Ollama/Gemma/Llama).
- **Function**: Converts the Answer Plan and Retrieved Context into natural language, strictly constrained by the evidence provided in Layer 4.

#### Layer 7: Self-Validation Loop
- **Mechanism**: LLM-as-a-Judge + Symbolic Consistency Checking.
- **Function**: Scrutinizes the generated response for hallucinations, factual drift, or tone violations before final delivery.

#### Layer 8: Explainability & SIEM Auditing
- **Persistence**: Deep PostgreSQL storage.
- **Function**: Serializes the entire state of Layers 0–7 into a **Reasoning Trace** (JSON). This trace is used by the *NeuroConsole* UI to provide full transparency to the end-user or auditor.

---

### 3. Operational Workflows

#### A. Chatbot Interface Workflow (Consumer Side)
1. **Query Entry**: User submits a query via the React-based Chat UI.
2. **Session Ignition**: System creates a `UserSession` and logs the IP/Device meta.
3. **Pipeline Execution**: The 8-layer pipeline runs (as described above).
4. **SSE Streaming**: The answer is streamed chunk-by-chunk to the user via Server-Sent Events (SSE).
5. **Human-in-the-loop (HITL)**: Users can view the *NeuroConsole* to see exactly why the AI made a specific decision, which rules were triggered, and which documents were cited.

#### B. Admin Console Workflow (Governance Side)
1. **System Health & Stats**: Real-time monitoring of query volume, model usage (tokens), and system latency.
2. **Knowledge Governance**: Administrators can upload, re-index, and manage the scope/access levels of internal documentation.
3. **Rule & Intent Management**: Direct editing of the production rules (`IF intent X THEN require doc Y`) and ontology hierarchies.
4. **Transactional Audit Explorer**: A deep-dive explorer into the PostgreSQL operational tables, allowing admins to inspect full reasoning traces for any historical query.
5. **Security Event Monitoring**: Real-time logging of "Unauthorized Access Attempts" or policy violations caught at Layer 0/3.

---

### 4. Conclusion
By decoupling the "Thinking" (Symbolic Expert System) from the "Speaking" (Generative LLM), this architecture provides a blueprint for safe, explainable AI in regulated industries. The integration of 10 distinct operational database tables ensures a total audit trail, making the system suitable for high-compliance documentation environments.
