# WellNexa AI — System Architecture Document

## 1. High-Level Architecture
WellNexa AI follows a **Modular Monolith** architecture designed for high cohesion, clear domain boundaries, low operational complexity, and optimal latency.

```mermaid
graph TD
    subgraph Client Tier [Cross-Platform Presentation]
        Flutter["📱 Flutter Client (Android, Web, Desktop)"]
    end

    subgraph Gateway & Security Tier
        FastAPIGateway["🚀 FastAPI API Gateway & Routers"]
        SecHeaders["🛡️ Security Headers & Rate Limiters"]
    end

    subgraph Business Logic Modules
        M1["Health & Vitals"]
        M2["Timeline Dispatcher"]
        M3["Document Vault"]
        M4["OCR & Extractor"]
        M5["Medicines & Adherence"]
        M6["Reminders Engine"]
        M7["Nutrition Tracker"]
        M8["Fitness & Lifestyle"]
        M9["Mental Wellness"]
        M10["AI Assistant Engine"]
        M11["Doctor Sharing Portal"]
        M12["Privacy & Audit Logging"]
    end

    subgraph Data & Storage Tier
        Postgres[(PostgreSQL 16 Relational Engine)]
        PgVector[(pgvector Clinical Vector Store)]
        DocVault[(Secure Encrypted File Vault)]
    end

    Flutter <-->|REST API + JWT Bearer| FastAPIGateway
    FastAPIGateway --> SecHeaders
    SecHeaders --> Business Logic Modules
    Business Logic Modules <--> Postgres
    M10 <--> PgVector
    M3 <--> DocVault
```

---

## 2. Architectural Layers
1. **Presentation Layer (Flutter)**: Material 3 design system, Riverpod state management, Dio HTTP client with automatic JWT token attachment and 401 unauthenticated interception.
2. **API & Security Layer (FastAPI)**: Pydantic v2 schema validation, Dependency Injection (`get_db`, `get_current_active_user`, `require_roles`), sliding-window rate limiters, and enterprise security headers (`HSTS`, `CSP`, `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`).
3. **Application Domain Modules**: 13 isolated domain services communicating through clean internal Python interfaces.
4. **AI & Clinical Guardrail Subsystem**: Context assembler, RAG knowledge retriever, physiological reference boundary checker, and prompt injection defense.
5. **Data Persistence Layer**: PostgreSQL 16 relational database with ACID guarantees, foreign key cascades, and `pgvector` extension for semantic guideline retrieval.
