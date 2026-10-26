# WellNexa AI — Cross-Platform Personal Healthcare and Wellness Management System

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Flutter](https://img.shields.io/badge/Flutter-3.19.0-02569B.svg?style=flat&logo=flutter)](https://flutter.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16_with_pgvector-336791.svg?style=flat&logo=postgresql)](https://www.postgresql.org)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB.svg?style=flat&logo=python)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**WellNexa AI** is a production-grade, cross-platform personal healthcare and wellness management system designed for comprehensive health tracking, medical document extraction, medication management, and evidence-grounded AI assistance.

---

## 🌟 Key Features

1. **Unified Health Profile & Vitals**: Complete vitals tracking with automatic BMI calculations, known allergies, chronic conditions, and lifestyle profiles.
2. **Centralized Health Timeline**: Single chronological audit trail uniting vitals, lab reports, prescriptions, workouts, and consultations.
3. **Medical Report OCR & Human Confirmation**: Complete Blood Count (CBC), Fasting/PP Glucose, Lipid Profile, and Thyroid Profile extractions with physiological reference range boundary flags (`NORMAL`, `LOW`, `HIGH`, `CRITICAL`).
4. **Medical Report Analyzer & Delta Comparisons**: Plain-language clinical explanations and historical delta comparisons across consecutive reports.
5. **Prescription & Medicine Manager**: Inventory stock tracking, dose logging (`TAKEN`, `MISSED`, `SKIPPED`), and dynamic Adherence Score calculations (`EXCELLENT`, `GOOD`, `NEEDS_ATTENTION`).
6. **Central Smart Reminder Engine**: Multi-category reminder scheduling (`MEDICINE`, `WATER`, `APPOINTMENT`, etc.) with user quiet-hours enforcement.
7. **Nutrition & Meal Tracking**: Nutritional reference database with automatic macro calculation and AI Meal Planner with diet preferences (`VEGETARIAN`, `KETO`, `JAIN`, etc.).
8. **Fitness & Daily Activity**: Workout tracking, step counts, sleep quality ratings, hydration, and habit check-in streaks.
9. **Mental Wellness Journal**: 1-5 mood rating, gratitude reflection, and AI Crisis Guardrails attaching 24/7 verified crisis helplines.
10. **Grounded AI Health Assistant (RAG)**: Multi-turn chat grounded in active patient baseline and WHO/ICMR clinical guidelines with emergency triage redirection.
11. **Doctor / Healthcare Professional Portal**: Time-bound access grants (1 hr to 30 days) with granular scope controls, instant kill-switch revocation, and physician consultation notes.
12. **Consent & Privacy Center**: Granular AI/research consent toggles and one-click JSON health data export archive (GDPR/HIPAA).
13. **Intelligent Health Dashboard**: High-performance home aggregation endpoint powering Flutter widgets.
14. **360-Degree AI Health Snapshot**: Multi-domain synthesis highlighting positive trends, areas for attention, and prioritized next best actions.
15. **In-App Notification Center**: Real-time unread badge counters and multi-channel dispatcher abstraction.
16. **Immutable Audit Logging**: Write-only append security log for compliance and patient transparency.

---

## 🚀 Quick Start Guide

### 1. Start Infrastructure via Docker Compose
```bash
docker compose up -d
```

### 2. Run Database Migrations
```bash
cd backend
alembic upgrade head
```

### 3. Seed Demonstration Data
```bash
python -m app.db.seed_demo_data
```
- **Demo Patient**: `patient@wellnexa.ai` / `Password123!`
- **Demo Doctor**: `doctor@wellnexa.ai` / `Password123!`

### 4. Run Backend API Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Interactive API documentation: `http://localhost:8000/docs`

### 5. Run Next.js Frontend (Website)
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:3000`. The frontend proxies `/api/*` to the backend at `http://127.0.0.1:8000`.

> Note: A legacy Flutter mobile client exists under `apps/mobile` and a Vite web client under `apps/web`; the supported website for this spec is the Next.js app in `/frontend`.

---

## 🧪 Running Automated Test Suite

```bash
cd backend
pytest -v
```

---

## 📖 Demonstration & Viva Guide
For a step-by-step 10-minute project presentation script, refer to [`docs/DEMO_WALKTHROUGH.md`](docs/DEMO_WALKTHROUGH.md).


## Architecture

Modular monolith: Next.js (App Router) frontend -> FastAPI backend -> PostgreSQL + pgvector. A separate Python worker process runs an asyncio loop for reminders, emails, and grant expiry. OCR via Tesseract (pytesseract + pdf2image), AI via OpenAI SDK (key from env), encryption via AES-GCM (cryptography).

## Setup from zero (docker-compose)

`ash
cp .env.example .env
docker compose up -d --build
`

Services: postgres (pgvector), api (runs alembic upgrade head then uvicorn), worker (asyncio loop), web (Next.js).

## Environment variables

See .env.example. Key: DATABASE_URL, SYNC_DATABASE_URL, SECRET_KEY, OPENAI_API_KEY, LLM_PROVIDER, LLM_MODEL, EMBEDDING_MODEL, ENCRYPTION_KEY, SMTP_HOST/PORT/USER/PASSWORD/FROM, UPLOAD_DIR.

## Seed data

`ash
docker compose exec api python -m app.db.seed_demo_data
`

## Migrations

`ash
docker compose exec api alembic upgrade head
`

## Worker

Runs as worker service. Locally: cd backend && python -m app.worker

## SMTP and LLM configuration

Set SMTP_* to enable email; otherwise sends are skipped/logged (no health data).
Set LLM_PROVIDER=openai and OPENAI_API_KEY for real LLM; default mock.
RAG ingestion: cd backend && python -m app.services.rag_ingest

## Tests

`ash
python scripts/run_tests.py
`

Playwright E2E: cd frontend && npx playwright install && npm run test:e2e

## Deployment notes

HTTPS in production via reverse proxy; secure cookies and CORS allow-list. Rotate encryption key via re-encryption script.
