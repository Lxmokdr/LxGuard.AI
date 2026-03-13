# Linked Open Data (LOD) & SPARQL Federation

This document describes the implementation and integration of Linked Open Data (LOD) within the Hybrid NLP-Expert Agent architecture.

## Overview
The system utilizes external knowledge from the **LOD Cloud** (specifically DBpedia) to enrich its local Knowledge Graph and Document RAG. This is used when internal sources (Tiers 1-4) are insufficient or when broad factual context is required.

## Components

### 1. `LODClient` (`engines/lod_client.py`)
The core interface for SPARQL federation.
- **Endpoint**: Defaults to `https://dbpedia.org/sparql`.
- **Functionality**:
    - Executes raw SPARQL queries via HTTP.
    - Implements specialized entity lookup (`get_entity_abstract`).
    - Handles URI normalization (e.g., `React` -> `React_(JavaScript_library)`).
    - Includes a lightweight fallback mechanism for common technical terms.

### 2. `HybridKnowledgeAgent` (`agents/hybrid_agent.py`)
The orchestrator for external-mode reasoning.
- **Logic**: Implements a "Hybrid Fallback" strategy:
    1. Local Docs (RAG)
    2. Local Ontology (Rules)
    3. **LOD Enrichment (DBpedia)**
    4. General LLM Knowledge

## API Integration

LOD is triggered via the **Streaming Chat API**:
- **Endpoint**: `POST /api/chat/stream`
- **Parameter**: `mode: "external"`
- **Flow**:
    ```mermaid
    sequenceDiagram
        User->>API: Chat Request (mode="external")
        API->>HybridKnowledgeAgent: ask(query)
        HybridKnowledgeAgent->>NLP: Extract Entity (Subject)
        HybridKnowledgeAgent->>LODClient: get_entity_abstract(Subject)
        LODClient->>DBpedia: SPARQL Query
        DBpedia-->>LODClient: RDF Data (Abstract)
        LODClient-->>HybridKnowledgeAgent: Plain Text
        HybridKnowledgeAgent->>LLM: Synthesize Answer
        LLM-->>API: Streamed Response
    ```

## Governance & Policy Filtering
The "policy-filtering" mentioned in the research paper is enforced through:
- **Internal Parameterization**: Users cannot supply arbitrary SPARQL; the system only executes pre-defined template queries for specific predicates (`dbo:abstract`, `rdfs:comment`).
- **Mode Isolation**: LOD is decoupled from the primary internal pipeline to prevent data leakage and ensure that only authorized entities are looked up externally.
