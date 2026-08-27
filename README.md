# WellNexa AI — Cross-Platform Personal Healthcare & Wellness System

[![Backend: FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com)
[![Frontend: Flutter](https://img.shields.io/badge/Frontend-Flutter-02569B.svg)](https://flutter.dev)
[![Database: PostgreSQL+pgvector](https://img.shields.io/badge/Database-PostgreSQL%20%2B%20pgvector-336791.svg)](https://github.com/pgvector/pgvector)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

WellNexa AI is a production-style, modular, cross-platform personal healthcare and wellness management system. It bridges the gap between fragmented health data and daily wellness by providing a unified health profile, human-verified OCR extraction for medical reports, prescription adherence tracking, smart reminders, nutrition & fitness tracking, privacy-controlled doctor sharing, and an AI health assistant.

---

## 🏗️ Architecture

- **Frontend**: Flutter + Dart (Riverpod, GoRouter, Dio, fl_chart) targeting Android & Web.
- **Backend**: Python 3.12+ FastAPI modular monolith with SQLAlchemy & async Alembic migrations.
- **Database**: PostgreSQL 16 with `pgvector` extension for structured clinical records & RAG embeddings.
- **AI & OCR**: PaddleOCR pipeline with human confirmation workflow + provider-agnostic RAG.

---

## 🚀 Quick Start (Local Development)

### 1. Prerequisites
- Python 3.12+
- Docker & Docker Compose
- Flutter SDK (for mobile/web app)

### 2. Environment Setup
```bash
# Clone the repository
git clone https://github.com/Ajaychaudhari09/Wellnexa.git
cd Wellnexa

# Copy environment variables
cp .env.example .env
```

### 3. Start Database & Backend with Docker
```bash
docker compose up --build
```
- API Documentation (Swagger): [http://localhost:8000/docs](http://localhost:8000/docs)
- Health Check: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

### 4. Run Backend Locally (Without Docker)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 5. Run Flutter Application
```bash
cd apps/mobile
flutter pub get
flutter run -d chrome # Or -d android
```

---

## 🧪 Running Tests
```bash
cd backend
pytest tests/
```

---

## 📅 Phased Implementation Roadmap
- [x] **Phase 0**: Repository & Development Foundation
- [ ] **Phase 1**: Database, Auth & Role-Based Access Control (RBAC)
- [ ] **Phase 2**: Unified Health Profile & Metrics
- [ ] **Phase 3**: Centralized Health Timeline
- [ ] **Phase 4**: Document Management (PDF/Images)
- [ ] **Phase 5**: OCR Pipeline (CBC, Glucose, Lipid, Thyroid)
- [ ] **Phase 6**: Medical Report Analyzer & Historical Trends
- [ ] **Phase 7**: Prescription & Medicine Manager (Adherence Scoring)
- [ ] **Phase 8**: Central Smart Reminder Engine
- [ ] **Phase 9**: Nutrition & AI Meal Tracking
- [ ] **Phase 10**: Fitness & Lifestyle Tracking
- [ ] **Phase 11**: Mental Wellness & Mood Journal
- [ ] **Phase 12**: AI Health Assistant (RAG + Safety Guardrails)
- [ ] **Phase 13**: Doctor / Healthcare Professional Portal
- [ ] **Phase 14**: Consent & Privacy Center (Granular Revocable Access)
- [ ] **Phase 15**: Intelligent Health Dashboard
- [ ] **Phase 16**: AI Health Snapshot
- [ ] **Phase 17**: Notification Infrastructure
- [ ] **Phase 18**: Immutable Audit Logging
- [ ] **Phase 19**: Flutter UI & Responsive Design System
- [ ] **Phase 20**: Security Review & Hardening
- [ ] **Phase 21**: Comprehensive End-to-End Testing
- [ ] **Phase 22**: Production Deployment & Release
