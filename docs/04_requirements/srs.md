# WellNexa AI — Software Requirements Specification (SRS)

## 1. Introduction
### 1.1 Purpose
This Software Requirements Specification (SRS) document details the functional and non-functional requirements for **WellNexa AI**, an integrated, cross-platform personal healthcare and wellness management platform for an MCA Capstone Project.

### 1.2 Document Conventions
- Requirements are uniquely identified using prefixes: `FR-xxx` (Functional Requirements) and `NFR-xxx` (Non-Functional Requirements).
- MoSCoW priorities: `MUST_HAVE`, `SHOULD_HAVE`, `COULD_HAVE`, `WONT_HAVE_NOW`.

### 1.3 Intended Audience
- Academic Evaluation Committee & Project Guides
- Software Architects & Full-Stack Developers
- System Quality Assurance & Security Auditors

---

## 2. Overall Description
### 2.1 Product Perspective
WellNexa AI operates as a cross-platform (Flutter) client connecting to a modular monolith FastAPI backend with a PostgreSQL/pgvector database.

### 2.2 User Classes and Characteristics
1. **Patient (User)**: General individual managing personal vitals, prescriptions, lab reports, workouts, and mood.
2. **Healthcare Professional (Doctor)**: Clinician accessing authorized, time-bound patient summaries and authoring consultation notes.
3. **System Administrator**: Compliance officer monitoring system health, audit logs, and security telemetry.

---

## 3. System Features & Functional Requirements Summary
- **Module 1: Authentication & RBAC (`FR-001` to `FR-005`)**: Secure login, registration, JWT rotation, role assignment.
- **Module 2: Health Profile & Vitals (`FR-006` to `FR-010`)**: Baseline metrics, auto-calculated BMI, chronic conditions, allergies.
- **Module 3: Health Timeline (`FR-011` to `FR-014`)**: Unified chronological event logging and filtering.
- **Module 4: Medical Documents & OCR (`FR-015` to `FR-020`)**: File storage, SHA-256 integrity, OCR parameter extraction, physiological flags, human confirmation.
- **Module 5: Prescriptions & Adherence (`FR-021` to `FR-025`)**: Medicine schedules, stock decrement, refill warnings, monthly percentage adherence scoring.
- **Module 6: Smart Reminders (`FR-026` to `FR-029`)**: Multi-category recurrence alerts with quiet-hours enforcement.
- **Module 7: Nutrition & Meals (`FR-030` to `FR-034`)**: Macro budget tracking, food item lookup, AI meal planner with diet filters.
- **Module 8: Fitness & Habits (`FR-035` to `FR-038`)**: Workout logging, step counts, sleep quality, hydration, habit check-in streaks.
- **Module 9: Mental Wellness (`FR-039` to `FR-041`)**: 1-5 mood score, gratitude notes, 24/7 crisis helpline attachment.
- **Module 10: AI Health Assistant (`FR-042` to `FR-045`)**: Grounded RAG multi-turn chat, active medication awareness, emergency triage redirection.
- **Module 11: Doctor Portal (`FR-046` to `FR-048`)**: Time-bound access grants (1 hr to 30 days), scope selection, instant kill-switch revocation, consultation notes.
- **Module 12: Consent, Privacy & Dashboard (`FR-049` to `FR-050`)**: Granular AI/research consent, immutable audit logging, GDPR/HIPAA JSON export, aggregated home dashboard.
