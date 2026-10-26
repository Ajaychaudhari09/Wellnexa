# FEATURE_STATUS.md

| Step | Feature | Working | Test that proves it | Command to reproduce |
|------|---------|---------|---------------------|----------------------|
| 2 | Auth (register/login/refresh) | yes | backend/tests/test_auth.py | `cd backend && pytest tests/test_auth.py -q` |
| 3 | Personal health profile + BMI | yes | backend/tests/test_profile.py | `cd backend && pytest tests/test_profile.py -q` |
| 4 | Report upload + OCR + timeline | yes | backend/tests/test_ocr_pipeline.py, test_report_analyzer.py, test_timeline.py | `cd backend && pytest tests/test_ocr_pipeline.py tests/test_report_analyzer.py tests/test_timeline.py -q` |
| 5 | AI assistant RAG/LLM | yes (mock provider by default) | backend/tests/test_ai_assistant.py, test_clinical_safety.py | `cd backend && pytest tests/test_ai_assistant.py tests/test_clinical_safety.py -q` |
| 6 | Prescription & medicines | yes | backend/tests/test_medicines.py | `cd backend && pytest tests/test_medicines.py -q` |
| 7 | Smart reminders | yes | backend/tests/test_reminders.py, test_notifications.py | `cd backend && pytest tests/test_reminders.py tests/test_notifications.py -q` |
| 8 | Nutrition planner | yes | backend/tests/test_nutrition.py | `cd backend && pytest tests/test_nutrition.py -q` |
| 9 | Fitness tracker | yes | backend/tests/test_fitness.py | `cd backend && pytest tests/test_fitness.py -q` |
| 10 | Mental wellness | yes | backend/tests/test_wellness.py | `cd backend && pytest tests/test_wellness.py -q` |
| 11 | Analytics & trends | yes | backend/tests/test_health_metrics.py | `cd backend && pytest tests/test_health_metrics.py -q` |
| 12 | Doctor portal & sharing | yes | backend/tests/test_doctor_portal.py | `cd backend && pytest tests/test_doctor_portal.py -q` |
| 13 | Appointments | yes | backend/tests/test_appointments.py | `cd backend && pytest tests/test_appointments.py -q` |
| 14 | Dashboard | yes | backend/tests/test_dashboard.py | `cd backend && pytest tests/test_dashboard.py -q` |
| 15 | Security & audit | yes | backend/tests/test_security_hardening.py, test_audit_logging.py, test_privacy.py | `cd backend && pytest tests/test_security_hardening.py tests/test_audit_logging.py tests/test_privacy.py -q` |

Notes:
- LLM provider defaults to `mock`. Set `LLM_PROVIDER=openai` and `OPENAI_API_KEY` for real LLM.
- OCR uses Tesseract when installed; otherwise falls back gracefully.
- Email uses SMTP settings; if unconfigured, sends are skipped/logged.
- Worker runs via `python -m app.worker` (asyncio loop, 60s poll).
- Frontend is Next.js (App Router) with pages for auth, dashboard, profile, reports, assistant. Other module pages are available in the legacy Vite client under `apps/web` and can be migrated incrementally.
