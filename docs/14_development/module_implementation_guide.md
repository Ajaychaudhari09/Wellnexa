# WellNexa AI — Module Implementation Guide

## 1. Directory & Package Structure
```text
backend/app/
├── core/               # Database, security, exceptions, middleware, rate limiter
├── models/             # SQLAlchemy 2.0 async domain models
├── modules/            # 13 Decoupled business domain packages
│   ├── auth/           # Login, registration, token rotation, RBAC
│   ├── health/         # Vitals, metrics, BMI calculator, allergies, conditions
│   ├── timeline/       # Centralized chronological event dispatcher
│   ├── documents/      # Secure document storage vault & SHA-256 validation
│   ├── reports/        # Medical report OCR pipeline & human confirmation
│   ├── medicines/      # Prescription management, dose logs & adherence
│   ├── reminders/      # Multi-category central reminder scheduler
│   ├── nutrition/      # Meal logging, macro budgets, AI meal planner
│   ├── fitness/        # Workouts, step counts, sleep & habit tracking
│   ├── wellness/       # Mood journal, gratitude, 24/7 crisis hotlines
│   ├── assistant/      # Grounded AI Assistant (RAG + safety filters)
│   ├── doctor/         # Doctor portal, time-bound sharing & consultations
│   ├── privacy/        # Consent management, access audit logs, JSON export
│   ├── dashboard/      # Home screen aggregation endpoint
│   ├── snapshot/       # 360-degree holistic AI Health Snapshot
│   └── notifications/  # In-App notification center & multi-channel dispatcher
└── main.py             # FastAPI entrypoint, middleware, and router mounts
```

## 2. Implementation Conventions
- **Asynchronous Operations**: All database I/O uses `async/await` with `AsyncSession`.
- **Strict Typing & Validation**: 100% of request and response payloads use Pydantic v2 schemas.
- **Relational Integrity**: Foreign keys enforce cascade deletions to guarantee zero orphaned records.
