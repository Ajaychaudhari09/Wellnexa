# WellNexa AI — Project Scope Statement

## 1. In-Scope Functional Modules
- **Authentication & RBAC**: JWT Access & Refresh token rotation, Argon2/bcrypt hashing, multi-role access control (`PATIENT`, `DOCTOR`, `ADMIN`).
- **Unified Health Profile & Vitals**: Demographics, allergies, chronic conditions, lifestyle targets, generic vitals tracking with auto-calculated BMI engine.
- **Centralized Health Timeline**: Normalized chronological event dispatcher uniting clinical, medication, and lifestyle events.
- **Medical Document Vault**: Encrypted file storage (PDF, PNG, JPEG), 10MB limit, SHA-256 integrity checksums.
- **Medical Report OCR & Confirmation**: Automated parameter extraction for CBC, Glucose, Lipid, and Thyroid panels with physiological reference range flags and human-in-the-loop confirmation.
- **Prescription & Medicine Manager**: Scheduled doses, inventory stock decrementing, refill warnings, dynamic monthly adherence scoring (`EXCELLENT`, `GOOD`, `NEEDS_ATTENTION`).
- **Central Smart Reminders**: Daily, weekly, monthly recurrence engine with quiet-hours enforcement.
- **Nutrition & Meal Tracker**: Food nutritional database, daily calorie/macro budget tracking, AI meal planner with diet preferences (`VEGETARIAN`, `KETO`, `JAIN`).
- **Fitness & Lifestyle Tracker**: Workout logging, step counts, sleep hours & sleep quality ratings, hydration tracking, habit check-in streaks.
- **Mental Wellness Journal**: 1-5 mood score, gratitude notes, and automated 24/7 crisis helpline attachment.
- **Grounded AI Health Assistant**: Multi-turn conversational chat with RAG over clinical guidelines, active medication awareness, and emergency symptom triage.
- **Doctor Portal**: Time-bound access grants (1 hr to 30 days), scope selection, instant revocation kill-switch, physician consultation notes.
- **Consent & Privacy Center**: Granular AI/research consent toggles, access audit logs, one-click portable JSON health data archive export (GDPR/HIPAA).
- **Intelligent Health Dashboard**: High-performance home aggregation endpoint powering Flutter widgets.
- **360-Degree AI Health Snapshot**: Multi-domain synthesis highlighting positive trends, attention areas, and next best actions.
- **Notification Infrastructure**: In-App Notification Center, real-time unread badge counter, multi-channel dispatcher abstraction.
- **Security & Compliance**: Security headers middleware, sliding-window rate limiters, prompt injection defense, append-only immutable audit logging.

## 2. Out-of-Scope (Boundaries & Non-Goals)
- Autonomous clinical disease diagnosis or treatment prescription.
- Direct integration with proprietary hospital Electronic Health Record (EHR) hardware systems (e.g. Epic/Cerner HL7 live bridges).
- Direct real-time pharmacy payment processing or delivery logistics.
- Telemedicine real-time video/audio calling (system provides structured clinical records and notes only).
