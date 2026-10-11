# Architecture Decision Record (ADR 003)
## Core Technology Stack Selection: FastAPI & Flutter

### Status: ACCEPTED

### Context
Selection of the primary backend API framework and cross-platform frontend UI toolkit.

### Decision
- **Backend**: Python 3.12 + FastAPI + SQLAlchemy 2.0 (Async) + Alembic.
- **Frontend**: Flutter 3.19 + Dart + Riverpod + GoRouter.

### Rationale
- **FastAPI**: Provides native asynchronous concurrency (`asyncio`), automatic Pydantic request validation, and self-documenting OpenAPI Swagger specifications.
- **Flutter**: Provides a single unified codebase compiling natively to Android, Web, and Desktop with consistent 60fps rendering, eliminating duplicate frontend development.
