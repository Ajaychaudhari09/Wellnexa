# WellNexa AI — Architectural Component Diagram

```mermaid
graph TD
    subgraph Presentation Layer [Flutter Cross-Platform Client]
        UI[Material 3 UI Screens]
        Route[GoRouter Shell]
        DioClient[Dio HTTP ApiClient + JWT Interceptor]
        SecStore[Secure Token Storage]
    end

    subgraph API Gateway & Security Layer [FastAPI Core]
        SecHeaders[Security Headers Middleware]
        RateLimit[Sliding-Window Rate Limiter]
        AuthRouter[Auth & RBAC Router]
    end

    subgraph Business Domain Modules
        DashMod[Dashboard Aggregator]
        HealthMod[Health Profile & Vitals]
        TimeMod[Central Timeline]
        DocMod[Medical Document Vault]
        OcrMod[OCR & Extraction Engine]
        MedMod[Medicines & Adherence]
        RemMod[Reminder Engine]
        NutMod[Nutrition Tracker]
        FitMod[Fitness & Habit Tracker]
        WellMod[Mood & Wellness Journal]
        DocPortal[Doctor Sharing Portal]
        PrivMod[Privacy & Audit Engine]
    end

    subgraph AI Intelligence Subsystem
        Assembler[Patient Context Assembler]
        SafetyGuard[Clinical Guardrail Checker]
        RAGRetriever[RAG Knowledge Retriever]
        SnapEngine[Health Snapshot Engine]
    end

    subgraph Persistence & Infrastructure Layer
        Postgres[(PostgreSQL 16 Relational Engine)]
        PgVector[(pgvector Clinical Embedding Store)]
        DocStorage[(Local/Cloud File Storage Vault)]
    end

    UI --> DioClient
    DioClient <--> SecHeaders
    SecHeaders --> RateLimit
    RateLimit --> AuthRouter
    AuthRouter --> Business Domain Modules
    Business Domain Modules <--> AI Intelligence Subsystem
    Business Domain Modules <--> Postgres
    AI Intelligence Subsystem <--> PgVector
    DocMod <--> DocStorage
```
