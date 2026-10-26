# Feature Status

Verified locally on 2026-10-26. “API tests” are FastAPI tests using in-memory SQLite; they verify module behavior and do not prove production Postgres, third-party APIs, live email, or OCR quality.

| Module | Verified behavior | Still incomplete or unverified |
|---|---|---|
| Accounts and roles | Patient registration/login, token flows, role checks; public role escalation is denied. | Email verification and password reset are not implemented; doctor account onboarding is not a complete approval workflow. |
| Health profile | Profile read/update works; name, phone, and emergency contact fields are encrypted at rest with AES-GCM. Legacy plaintext profile values still read. | Other clinical data tables are not comprehensively encrypted; profile schema does not match every item in the pasted specification. |
| Documents, reports, OCR | Upload and report review/confirmation APIs pass synthetic lifecycle tests. | No real scanned-file accuracy or asynchronous OCR worker acceptance test. |
| Assistant and AI | Assistant sessions, local response engine, and safety/prompt-injection tests pass. | No verified provider-backed RAG citations or real LLM request in this run. |
| Medicines | Medication lifecycle, dose logging, and adherence APIs pass tests. | No pharmacy integration. |
| Reminders and notifications | Reminder APIs pass; notification list, unread count, single/bulk mark-read and cross-user ownership checks pass. UI has “Mark as read” and “Mark all as read.” | Real scheduled delivery and SMTP receipt were not tested. Worker reliability/time-zone behavior needs more work. |
| Nutrition | Food lookup and meal logging APIs pass tests. | USDA data import and production nutrition coverage are not implemented/verified. |
| Fitness | Workouts, activity and habit APIs pass tests. | Wearable integration and weekly email delivery are not implemented/verified. |
| Wellness | Mood logging, trends and crisis safety behavior pass tests. | No external crisis-service integration. |
| Analytics and dashboard | Metrics/BMI and dashboard aggregation tests pass; Next dashboard requests live API data. | Requested chart/date-range analytics UI is incomplete. |
| Doctor sharing | Requires patient consent, a named active/verified doctor, and a time-bound grant; portal is role-gated and revocation is tested; access reads are audited. | No full provider onboarding or production expiry/consent audit. |
| Appointments | Appointment lifecycle API test passes. | Proposal/acceptance email and calendar integrations are not verified. |
| Privacy and audit | Consent, export, deletion, and audit API tests pass; user data access is owner-scoped. | Not a compliance certification; complete data encryption and retention enforcement need further work. |

## Checks run

- Backend suite: **34 passed**, including API module tests, IDOR/security tests, and mocked SMTP STARTTLS tests.
- Frontend production build: **passed**; all 13 Next.js routes compiled.
- Playwright smoke tests: **2 passed** (landing page and notification single/bulk mark-read flow using mocked API responses).
- Local API smoke check: startup, `/health`, `/`, and `/api/v1/health` passed against the configured local SQLite database.
- Docker Compose/PostgreSQL, real SMTP delivery, OpenAI provider calls, and full browser workflows: **not run**. Docker was unavailable; SMTP password was intentionally left blank after it was pasted into chat.

## Security notes

- Public registration cannot assign doctor/admin roles. Doctor record reads require an authenticated doctor account with a patient grant; grant access defaults off until the patient opts in. Notification updates are restricted to their owner.
- HTTPS responses receive HSTS; local HTTP does not. Run behind HTTPS in deployment.
- Only selected profile PII and assistant message content are encrypted in application storage today. Do not store real patient records in a deployment until encryption coverage, key rotation, backups, access controls, and retention have been reviewed.
- The Gmail app password was exposed in the conversation. Revoke it in Google, create a replacement, and enter it locally as `EMAIL_PASS` in the ignored `.env` files. It is not written in this repository or environment files.
