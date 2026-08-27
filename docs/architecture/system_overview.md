# WellNexa AI — System Architecture & Design Overview

## 1. Architectural Style
WellNexa AI follows a **Modular Monolith** architecture designed for reliability, strict data ownership, auditability, and clear separation of domain concerns.

```text
                    WELLNEXA AI

       ┌─────────────────────────────────────┐
       │      FLUTTER CROSS-PLATFORM APP     │
       │   Android • Web • Windows/Linux*    │
       └──────────────────┬──────────────────┘
                          │ HTTPS / REST (JWT)
       ┌──────────────────▼──────────────────┐
       │         FASTAPI BACKEND             │
       │                                     │
       │ Auth • RBAC • Health APIs           │
       │ Documents • Reminders • Analytics   │
       │ Notifications • Audit Logs          │
       └───────┬──────────────┬──────────────┘
               │              │
     ┌─────────▼─────┐  ┌────▼───────────────┐
     │ PostgreSQL    │  │ Python AI Services │
     │ + pgvector    │  │ OCR • RAG • ML     │
     └───────────────┘  │ CV optional        │
                        └─────────┬──────────┘
                                  │
                     ┌────────────▼───────────┐
                     │ Object/File Storage    │
                     │ Reports/Prescriptions  │
                     └────────────────────────┘
```

## 2. Core Architectural Principles
1. **Health Management Boundary**: WellNexa AI provides health tracking, organization, educational summaries, and informational guidance. It does not provide medical diagnoses or prescriptions.
2. **Human-in-the-Loop OCR**: Extracted values from medical documents are presented to the user for validation/correction prior to persisting to clinical metrics.
3. **Data Isolation & Time-Bound Sharing**: Healthcare professionals only access patient records explicitly selected by the patient with an enforced expiry duration.
4. **Immutable Audit Trail**: All authentication events, document access, data sharing, and AI queries generate immutable audit logs.
