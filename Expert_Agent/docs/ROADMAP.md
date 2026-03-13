# Enterprise v2 Architecture: Hybrid NLP-Expert Agent

**Status**: Draft / Specification
**Target**: Production-Ready Regulated Enterprise System

## 1. Architecture Delta

We are transitioning from a **Linear Pipeline** to a **Governed Decision Engine**.

| Existing System | Enterprise v2 Upgrade |
| :--- | :--- |
| **Flow** | Linear (Layer 1 -> 8) | **Arbitrated** (Authority checks at every step) |
| **Authority** | Implicit (Code logic in `HybridPipeline`) | **Explicit** (`DecisionAuthority` module) |
| **Logic** | "Best Effort" | **Contractual** (`KnowledgeContract` invariants) |
| **Retrieval** | Text Chunks | **Evidence Objects** (Lifecycle & Authority aware) |
| **Audit** | JSON Logs (Trace) | **Relational DB** (Regulatory Compliance) |
| **Refusal** | `SecurityEnforcer` only | **First-Class Refusal** (Structured rejection logic) |

---

## 2. New Core Modules List

The following modules will be added to the `Expert_Agent/` core:

1.  **`decision_authority.py`**
    *   **Role**: The Supreme Court of the system. Enforces the "Decision Priority Hierarchy".
    *   **Responsibility**: Resolves conflicts between Rules, RBAC, and NLP. Deterministic arbitration.
2.  **`knowledge_contracts.py`**
    *   **Role**: The Law. Defines machine-enforced invariants.
    *   **Responsibility**: Validates objects (Answers, Docs) against strict schema and logic guarantees.
3.  **`refusal_logic.py`**
    *   **Role**: The Gatekeeper.
    *   **Responsibility**: Standardized exceptions and handling for "Why I cannot answer".
4.  **`schema.sql`**
    *   **Role**: The Ledger.
    *   **Responsibility**: Database definitions for long-term auditability.

---

## 3. Execution Flow (Textual)

```text
QUERY RECEIVED
   ▼
1. AUTH & CONTEXT
   - Load User, Role, Permissions (DB)
   - Initialize Session
   ▼
2. DECISION AUTHORITY (Pre-Check)
   - Check Global Security Policies (PII, Blocklists)
   - Check RBAC for "Query Access"
   -> IF FAIL: Return Refusal(Security)
   ▼
3. NLP & INTENT RECOGNITION
   - Extract Intent & Entities
   ▼
4. DECISION AUTHORITY (Arbitration)
   - Consult Ontology (Is intent valid?)
   - Consult Rule Engine (Is intent allowed for User?)
   - Resolve NLP Confidence vs. Rule Constraints
   -> IF FAIL: Return Refusal(Policy)
   ▼
5. EVIDENCE RETRIEVAL
   - Filter Docs by Authority Level (Rule-based)
   - Retrieve Evidence Objects
   - Validate Contracts (Expiration, Version)
   -> IF Insufficient Evidence: Return Refusal(Evidence)
   ▼
6. ANSWER PLANNING
   - Generate Plan based on `KnowledgeContracts`
   ▼
7. GENERATION (LLM)
   - Render Answer (Strictly grounded)
   ▼
8. DECISION AUTHORITY (Final Review)
   - Validate Answer against Plan
   - Check Hallucinations & Forbidden Terms
   -> IF FAIL: Return Refusal(Safety)
   ▼
9. PERSISTENCE
   - Write Trace to SQL DB
   - Update Metrics
   ▼
RESPONSE SENT
```

---

## 4. Admin Capabilities Map

| Feature | Current (v1) | Upgrade (v2) |
| :--- | :--- | :--- |
| **Rule Editing** | Edit YAML/DSL | **Version Control & Rollback** |
| **Impact Analysis** | None | **Simulation / Blast Radius** |
| **Observability** | View Logs | **Drift Detection & Analytics** |
| **Data Management** | Markdown Files | **Lifecycle Management** (Review/Approve docs) |

---

## 5. Failure & Refusal Scenarios

The system explicitly handles these "No Answer" states:

1.  **`Refusal.SECURITY`**: PII detected, IP ban, or injection attempt.
2.  **`Refusal.RBAC`**: Intent recognized, but User lacks specific permission.
3.  **`Refusal.ONTOLOGY`**: Intent is deprecated, mutually exclusive, or incompatible.
4.  **`Refusal.EVIDENCE`**: Documents exist but score < threshold, or are expired.
5.  **`Refusal.UNCERTAINTY`**: NLP confidence < `MIN_CONFIDENCE` (and no Override Rule).
6.  **`Refusal.SAFETY`**: Output violated safety checks (Hallucination).

---

## 6. Enterprise Qualification

This architecture qualifies as **Enterprise-Grade** because:
*   **Determinism**: Rules *always* beat probability.
*   **Auditability**: Every decision is recorded in a queryable SQL format.
*   **Safety**: "Fail-Safe" design. If any contract is violated, the system refuses to answer rather than guessing.
*   **Independence**: Zero reliance on cloud APIs or external trusted parties.
