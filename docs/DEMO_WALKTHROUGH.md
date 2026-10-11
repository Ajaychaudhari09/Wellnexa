# WellNexa AI — Project Demonstration & Viva Presentation Guide

**Project Title**: WellNexa AI: Cross-Platform Personal Healthcare and Wellness Management System  
**Tech Stack**: FastAPI (Python 3.12), PostgreSQL + `pgvector`, SQLAlchemy (Async), Alembic, Flutter (Dart), Pytest

---

## 🎯 1. Introduction & Executive Summary (1 Minute)

> *"WellNexa AI is an enterprise-grade, cross-platform personal healthcare and wellness management system. It solves the fragmentation problem in digital health by integrating medical reports (OCR), prescriptions with dynamic adherence tracking, smart reminders, nutrition & fitness logging, mental wellness journaling, grounded AI health assistance (RAG), and a secure time-bound Doctor Portal into one unified, patient-centric ecosystem."*

---

## 🚀 2. System Architecture & Key Modules (2 Minutes)

Show the modular monolith architecture:
1. **Core Database & Security**: PostgreSQL with UUID primary keys, Argon2 hashing, JWT access/refresh token rotation, security headers, rate limiting, and immutable append-only audit logging.
2. **Medical Report OCR & Extraction Engine**: Extracts CBC, Fasting/PP Glucose, Lipids, and Thyroid panels with physiological reference range boundary flags (`NORMAL`, `LOW`, `HIGH`, `CRITICAL`) and human-in-the-loop confirmation.
3. **Prescription & Medicine Manager**: Automatic inventory stock decrementing upon logging doses and dynamic Adherence Score calculations (`EXCELLENT`, `GOOD`, `NEEDS_ATTENTION`).
4. **AI Health Assistant (RAG + Clinical Guardrails)**: Multi-turn chat grounded with patient baseline (active medications, allergies, vitals) and WHO/ICMR guidelines, with strict emergency red-flag triage, dosage refusal, and prompt injection defense.
5. **Doctor & Professional Portal**: Patient-controlled time-bound access links/QR codes with instant kill-switch revocation and physician consultation note synchronization.
6. **Intelligent Health Dashboard**: Single high-performance home endpoint aggregating all 13 health widgets.

---

## 💻 3. Live Demonstration Walkthrough (5 Minutes)

### Step 1: Pre-Seeded Accounts
- **Patient**: `patient@wellnexa.ai` / `Password123!`
- **Doctor**: `doctor@wellnexa.ai` / `Password123!`

### Step 2: Intelligent Home Dashboard
- Open the Flutter App or navigate to `http://localhost:8000/docs`.
- Showcase the **Home Dashboard**:
  - Greeting with user blood group.
  - Today's medicine checklist (taken vs pending doses).
  - Vitals & BMI categorization.
  - Daily calorie & hydration progress.
  - 30-day medication adherence score.

### Step 3: Medical Report OCR & Timeline
- Showcase the **Medical Document Upload & Confirmation**:
  - View extracted lipid parameters (Total Cholesterol, HDL, LDL, Triglycerides).
  - Show how confirmed reports automatically generate `REPORT_CONFIRMED` events on the central **Health Timeline**.

### Step 4: AI Health Assistant Interaction
- Ask a context-aware question: *"What dietary adjustments help manage my cholesterol and active Metformin?"*
- Observe how the AI assistant recognizes active medications and cites clinical guidelines.
- Ask an acute emergency question: *"I am experiencing severe chest pain and left arm numbness."*
- Observe the immediate Emergency Triage redirection with emergency hotline numbers (112/911).

### Step 5: Doctor Portal Time-Bound Sharing
- Patient generates a 24-hour access pass.
- Log in as Doctor or query `/api/v1/doctor/patient/{id}/summary?token={token}` to view the clinical summary.
- Post a doctor consultation note and show that it appears on the patient's timeline.
- Patient clicks **Revoke Access**; subsequent doctor access is blocked (`403 Forbidden`).

### Step 6: Consent & Health Data Export
- Navigate to **Consent & Privacy Center**.
- Click **Export Health Data (JSON)** to download the complete portable medical record (GDPR/HIPAA).

---

## 🛡️ 4. Clinical Safety & Legal Boundaries
- **Core Principle**: Educational health management, trend visualization, and routine tracking only.
- **Strict Non-Diagnostic Policy**: Clear medical disclaimers on all AI outputs; direct disease diagnosis and prescription alterations are strictly refused.

---

## 📊 5. Summary of Test Coverage
- **100% Phase Completion**: 23 comprehensive integration and unit test suites covering the entire end-to-end lifecycle.
