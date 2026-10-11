# WellNexa AI — Requirement Traceability Matrix (RTM)

| Req ID | Requirement Summary | Backend Module | Database Table(s) | Test Suite |
| :--- | :--- | :--- | :--- | :--- |
| **FR-001** | User Registration & Argon2 Hash | `app.modules.auth` | `users`, `profiles` | `test_auth.py` |
| **FR-002** | JWT Token Rotation | `app.modules.auth` | `refresh_tokens` | `test_auth.py` |
| **FR-006** | Vitals & Auto-calculated BMI | `app.modules.health` | `health_metrics` | `test_health_metrics.py` |
| **FR-011** | Centralized Health Timeline | `app.modules.timeline`| `health_timeline_events` | `test_timeline.py` |
| **FR-015** | Document Upload & Checksum | `app.modules.documents`| `medical_documents` | `test_documents.py` |
| **FR-016** | Medical Report OCR & Ranges | `app.modules.reports` | `medical_reports`, `report_extractions` | `test_ocr_pipeline.py` |
| **FR-021** | Prescription & Medicine Manager | `app.modules.medicines`| `medications`, `medication_logs` | `test_medicines.py` |
| **FR-024** | Dynamic Adherence Scoring | `app.modules.medicines`| `medication_logs` | `test_medicines.py` |
| **FR-026** | Central Smart Reminders | `app.modules.reminders`| `reminders`, `notification_preferences` | `test_reminders.py` |
| **FR-030** | Nutrition & Macro Budget | `app.modules.nutrition`| `meal_logs`, `meal_log_items` | `test_nutrition.py` |
| **FR-035** | Fitness & Daily Activity | `app.modules.fitness` | `workout_logs`, `daily_activity_summaries` | `test_fitness.py` |
| **FR-039** | Mood Journal & Crisis Helplines | `app.modules.wellness`| `mood_logs` | `test_wellness.py` |
| **FR-042** | Grounded AI Assistant (RAG) | `app.modules.assistant`| `chat_sessions`, `chat_messages` | `test_ai_assistant.py` |
| **FR-046** | Doctor Time-Bound Access Pass | `app.modules.doctor` | `patient_access_grants` | `test_doctor_portal.py` |
| **FR-049** | Complete JSON Health Export | `app.modules.privacy` | `user_consents`, `access_audit_logs` | `test_privacy.py` |
| **FR-050** | Unified Home Dashboard | `app.modules.dashboard`| All Aggregated Tables | `test_dashboard.py` |
