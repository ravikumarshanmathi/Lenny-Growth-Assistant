# Architecture: The Lenny Growth Assistant

> **Status:** DRAFT — Phase 1 Skeleton  
> **Last Updated:** 2026-10-10

---

## 1. Architecture Overview
### 1.1 System Context Diagram (C4 Level 1)
<!-- User → Lenny Assistant → Transcript Corpus / LLM Providers / PostgreSQL -->

### 1.2 Container Diagram (C4 Level 2)
<!-- Frontend (React/Vite) → Backend (FastAPI) → PostgreSQL (pgvector) → Ollama/Cloud LLMs -->

### 1.3 Technology Stack Summary
<!-- Reference Phase 0 §2.1 Technology Stack Matrix -->

## 2. Backend Architecture
### 2.1 FastAPI Application Structure
### 2.2 API Design & Error Contracts
### 2.3 Middleware Pipeline
### 2.4 Dependency Injection Pattern

## 3. Agent & LLM Integration
### 3.1 Provider Abstraction Layer (ADR-001)
### 3.2 Agent Orchestration Flow
### 3.3 Tool Definitions (retrieval, essay, artifact)
### 3.4 Prompt Engineering Strategy

## 4. RAG Pipeline
### 4.1 Ingestion Pipeline (ADR-002)
### 4.2 Chunking Strategy
### 4.3 Embedding Strategy (provider-matched)
### 4.4 Retrieval & Re-ranking
### 4.5 Citation Assembly

## 5. Data Layer
### 5.1 PostgreSQL Schema
### 5.2 pgvector Configuration
### 5.3 Migration Strategy (Alembic)
### 5.4 Connection Pooling & Resilience

## 6. Frontend Architecture
### 6.1 Component Hierarchy
### 6.2 State Management
### 6.3 SSE Streaming Integration
### 6.4 Artifact Rendering Pipeline (ADR-003)

## 7. Security Architecture
### 7.1 Artifact Isolation (3-layer model)
### 7.2 Content Security Policy
### 7.3 Input Validation & Sanitization

## 8. Deployment Architecture
### 8.1 Docker Compose Topology
### 8.2 Environment Configuration
### 8.3 Health Checks & Observability

## 9. ADR Index
### 9.1 ADR-001: Provider Toggle
### 9.2 ADR-002: RAG Pipeline
### 9.3 ADR-003: Artifact Security
