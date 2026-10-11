# Architecture Decision Record (ADR 001)
## Selection of Modular Monolith over Distributed Microservices

### Status: ACCEPTED

### Context
When designing WellNexa AI for an MCA Capstone and production healthcare platform, we evaluated whether to build a distributed microservices architecture or a modular monolith.

### Decision
We selected a **Modular Monolith** architecture implemented in FastAPI.

### Rationale
1. **Elimination of Distributed Network Overhead**: In a health platform, aggregating home dashboard data across 13 domains (medicines, vitals, reminders, reports) takes $<200\text{ms}$ in a single async process, whereas microservices would introduce latency and partial network failure risks.
2. **Transactional Integrity (ACID)**: Critical medical operations (e.g. confirming an OCR lab report must atomically write biomarkers, update the health timeline, and create an audit log) benefit from native PostgreSQL transactions without complex distributed two-phase commits (Saga patterns).
3. **Operational Simplicity for Capstone & Deployment**: A single Docker container handles all domain routers, vastly simplifying local student testing, CI/CD, and deployment.
