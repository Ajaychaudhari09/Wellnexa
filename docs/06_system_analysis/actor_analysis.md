# WellNexa AI — Actor Analysis & System Boundaries

```mermaid
graph LR
    subgraph External Actors
        P[👤 Patient / Consumer]
        D[👨‍⚕️ Healthcare Professional]
        A[🛡️ System Administrator]
        E[🚨 Emergency Services / Crisis Hotlines]
    end
    
    subgraph WellNexa AI System Boundary
        API[FastAPI Modular Monolith API Layer]
        AI[RAG Intelligence & Guardrails Engine]
        DB[(PostgreSQL 16 + pgvector)]
        FS[Medical Document Vault Storage]
    end
    
    P <-->|Flutter Mobile/Web/Desktop| API
    D <-->|Time-Bound Web Review| API
    A <-->|Compliance & Telemetry Audit| API
    AI <--> API
    API <--> DB
    API <--> FS
    AI -.->|Redirection Trigger| E
```

### Primary Actors
1. **Patient (User)**: Authenticated individual with full sovereign ownership over their profile, documents, vitals, prescriptions, and sharing permissions.
2. **Healthcare Professional (Doctor)**: Authenticated clinician or holder of a valid time-bound token granted temporary read access to structured summaries and consultation note recording.
3. **System Administrator**: Compliance officer with elevated privileges to inspect audit logs and monitor server health without access to unencrypted patient clinical records.
