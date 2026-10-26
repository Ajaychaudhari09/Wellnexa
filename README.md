# WellNexa AI

WellNexa is a health education and personal health management application. It does not diagnose, treat, or prescribe. AI content must be treated as educational and reviewed with a qualified healthcare professional.

## Architecture

- Next.js 14 App Router frontend (`frontend`)
- FastAPI API (`backend/app`)
- PostgreSQL 16 with pgvector, SQLAlchemy, and Alembic
- Separate asyncio worker process (`python -m app.worker`)
- Tesseract OCR and Poppler PDF rendering in the backend image
- OpenAI SDK for configured AI calls; SMTP through Python `smtplib`

## Prerequisites

Install Docker Desktop with Compose and ensure `docker` is on PATH for the PostgreSQL stack. Configure an OpenAI API key and SMTP credentials for provider features. The local API can also use an `aiosqlite` URL for development, but production configuration is PostgreSQL. Docker was unavailable during this verification; the configured local SQLite database and API health check were reachable.

## First startup

1. Copy `.env.example` to `.env`.
2. Replace every `CHANGE_ME` value. Use strong random values for `SECRET_KEY`, the database password, and `ENCRYPTION_KEY`. Generate the encryption key with:

   ```powershell
   python -c "import base64,secrets; print(base64.b64encode(secrets.token_bytes(32)).decode())"
   ```

3. Set a valid `OPENAI_API_KEY`, `LLM_MODEL`, and `EMBEDDING_MODEL`. SMTP settings accept either `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_SECURE`, `EMAIL_USER`, `EMAIL_PASS`, `EMAIL_FROM_NAME`, `EMAIL_FROM_ADDRESS`, `SUPPORT_EMAIL` or their `SMTP_*` aliases. For Gmail on port 587, use `EMAIL_SECURE=false`; the client still upgrades with STARTTLS before authentication. Keep the app password in your local ignored `.env` file and rotate it if it has been shared.
4. Start the four services:

   ```powershell
   docker compose up --build
   ```

The API service runs `alembic upgrade head` before Uvicorn starts. PostgreSQL data persists in the `postgres_data` volume; uploads are stored under `storage/uploads`. The API liveness check is `http://localhost:8000/health`; its database health check is `http://localhost:8000/api/v1/health`. The web UI is `http://localhost:3000` and API docs are `http://localhost:8000/docs`.

Compose starts a real OpenAI client configuration; AI-dependent operations fail with a provider error if the key or model access is invalid. SMTP delivery similarly requires a reachable configured server. The app does not silently substitute fake provider responses.

## Local development

With PostgreSQL running and `.env` configured, in one terminal:

```powershell
cd backend
python -m pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

In another terminal:

```powershell
cd backend
python -m app.worker
```

And for the frontend:

```powershell
cd frontend
npm ci
npm run dev
```

## Database and data

Migrations live in `backend/alembic/versions`. To apply them manually, run `alembic upgrade head` from `backend`. There is no automatic demo patient seed during API startup. The existing `app.db.seed_demo_data` script contains synthetic health data and should only be used in an isolated development database.

## Tests

Backend unit/API suite (dependencies include the test client and SQLite driver):

```powershell
cd backend
pytest -q
```

Frontend production build:

```powershell
cd frontend
npm ci
npm run build
```

Playwright E2E is available with `npm run test:e2e` after installing browsers and starting the API and web app. Backend tests use in-memory SQLite; SMTP tests mock the transport and do not send email. These checks do not prove PostgreSQL, real SMTP delivery, scanned-document OCR accuracy, or external LLM integration. See `FEATURE_STATUS.md` for tested behavior and gaps.

## Known implementation limits

The repository has feature modules and API routes beyond the current Next.js screens, but the full pasted 16-step acceptance suite is not complete. In particular, account email verification/reset, complete private-data encryption, provider-backed RAG citations, OCR background processing, reminder delivery guarantees, food-data ingestion, and comprehensive feature UI/tests require further work. Review `FEATURE_STATUS.md`; do not treat previously marked features as proven by real service tests.
