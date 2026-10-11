# WellNexa AI — Indexing & Database Migration Strategy

## 1. Indexing Strategy for Latency Optimization
- **Foreign Key Indexes**: Every `user_id`, `report_id`, and `medication_id` column has a dedicated B-tree index to accelerate relational joins and cascading deletes.
- **Composite Time-Series Indexes**:
  - `(user_id, recorded_at DESC)` on `health_metrics` to optimize historical trend chart queries.
  - `(user_id, occurred_at DESC)` on `health_timeline_events` for fast timeline pagination.
  - `(user_id, logged_date DESC)` on `meal_logs`, `workout_logs`, and `mood_logs`.
- **Token Lookup Indexes**: Unique B-tree index on `patient_access_grants.access_token` for $O(1)$ token verification.

## 2. Database Migration Management with Alembic
- All database schema modifications are version-controlled in `backend/alembic/versions/` using asynchronous SQLAlchemy migration scripts (`001_initial_schema.py` through `014_notification_infrastructure.py`).
- Single-command upgrade path: `alembic upgrade head`.
