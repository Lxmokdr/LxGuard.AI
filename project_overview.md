# LxGuard.AI Project Overview

## Project Description
LxGuard.AI is a Hybrid Neuro-Symbolic Conversational Architecture designed for enterprise knowledge retrieval in regulated environments. It combines Large Language Models (LLMs) with Symbolic Reasoning and Formal Ontologies to ensure grounded, compliant, and hallucination-resistant responses.

## Backend Architecture

### Core Backend: Expert_Agent
The main backend is located in the `Expert_Agent/` directory and implements an 8-layer neuro-symbolic pipeline:

#### 8-Layer Architecture
1. **Security Layer**: PII detection, redaction, and prompt injection filtering
2. **NLP Core Layer**: Probabilistic semantic parsing and intent hypothesis generation using spaCy
3. **Expert Agent Layer**: Deterministic validation using formal ontology and production rules
4. **Intent Arbitration Layer**: Conflict resolution between NLP and symbolic rules, including off-topic guard
5. **Retrieval Layer**: Multi-tier retrieval (Symbolic filtering + Semantic ranking with pgvector)
6. **Answer Planning Layer**: Structured answer contract creation
7. **Generation Layer**: Controlled LLM synthesis using local Ollama
8. **Validation Layer**: Self-critique and quality checks

#### Key Components
- **API**: FastAPI server with streaming chat endpoints (`/api/chat/stream`)
- **Database**: PostgreSQL with pgvector for semantic search and RDF graph for knowledge representation
- **Agents**: Expert agents for symbolic reasoning, validation, and hybrid knowledge retrieval
- **Engines**: Retrieval engine, LOD client (DBpedia), Ollama client
- **Services**: Document indexing with paragraph-aware chunking, ontology management, real-time knowledge sync
- **Configuration**: Ontology definitions, answer templates, audit schemas

#### Answer Modes
- `full`: Complete 8-layer pipeline for project-specific answers
- `external`: Hybrid agent with LOD (Linked Open Data) fallback
- `llm`: Direct LLM generation

#### Technologies
- Python/FastAPI
- SQLAlchemy with PostgreSQL
- spaCy for NLP
- pgvector for semantic search
- Ollama for local LLM
- Alembic for database migrations

## Frontend Projects

### 1. Admin Frontend (`admin-frontend/`)
**Technology**: Next.js 15 with TypeScript
**Purpose**: Administrative console for system management

#### Features
- User management and RBAC
- Rule configuration and ontology management
- Document indexing and knowledge base administration
- System monitoring and audit logs
- License management integration

#### Key Dependencies
- React 18
- Next.js 15
- TailwindCSS
- shadcn/ui components
- React Table for data display
- Axios for API communication
- React Hook Form for forms

### 2. Chatbot Frontend (`chatbot-frontend/`)
**Technology**: React + TypeScript with Vite
**Purpose**: User-facing chat interface with real-time reasoning visualization

#### Features
- Real-time chat with streaming responses
- Neuro-Console: 8-layer reasoning visualization
- Confidence scores and processing time display
- Rule trace visualization
- Knowledge source attribution
- Validation status display

#### Key Dependencies
- React 18
- Vite for build tooling
- TailwindCSS
- shadcn/ui components
- React Query for data fetching
- Axios for API communication


### Vendor Platform (`vendor_platform/`)
**Purpose**: License management and vendor control system
**Components**:
- `vendor_api`: FastAPI license server
- `vendor_dashboard`: Next.js admin dashboard for license management
- `vendor_db`: Dedicated PostgreSQL database

This is a separate system for managing enterprise licenses and is not part of the main application deployment.

### Documentation (`docs/`)
Contains comprehensive documentation including:
- Technical architecture details
- Enterprise deployment guides
- Anti-fraud measures
- LOD integration
- Internal credit approval processes

### Scripts and Configuration
- Root-level scripts for cache management, admin creation, PDF extraction
- Docker Compose for full-stack deployment
- Database seeding scripts
- Test scripts for latency measurement

## Deployment
The system is containerized using Docker and can be deployed via:
- Docker Compose for development
- Enterprise deployment with license activation
- Hugging Face Spaces integration
- Vercel deployment for frontends

## Security Features
- RBAC (Role-Based Access Control)
- PII filtering and redaction
- Prompt injection protection
- Off-topic guard
- Comprehensive audit logging
- License-based access control</content>
<parameter name="filePath">/home/lxmix/Downloads/projetiia/projet/project_overview.md