# WellNexa AI — Database & Entity Architecture

## 1. Normalized Relational Schema
WellNexa avoids giant unindexed JSON blobs and uses normalized tables:
- `users`, `roles`, `user_roles`, `refresh_tokens`, `profiles`
- `health_metrics`, `health_metric_types`, `allergies`, `medical_conditions`, `health_goals`
- `medical_documents`, `medical_reports`, `report_extractions`, `report_metrics`
- `prescriptions`, `medications`, `medication_schedules`, `medication_logs`
- `food_entries`, `meal_plans`, `fitness_logs`, `sleep_logs`, `water_logs`
- `mood_entries`, `journal_entries`
- `appointments`, `reminders`, `reminder_schedules`, `reminder_logs`
- `health_timeline_events`
- `professional_profiles`, `professional_patient_access`, `consent_records`
- `ai_conversations`, `ai_messages`, `ai_document_references`
- `audit_logs`, `notifications`

## 2. Vector Search (pgvector)
Embeddings for medical documents and knowledge base chunks are stored directly in PostgreSQL using `pgvector` with cosine similarity (`vector_cosine_ops`) indexing.
