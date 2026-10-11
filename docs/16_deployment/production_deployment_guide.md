# WellNexa AI — Production Deployment Guide

## 1. Prerequisites
- Docker Engine 24.0+ and Docker Compose v2.0+
- Python 3.12+ (for local CLI tooling)
- Flutter 3.19+ (for mobile and web builds)

## 2. Single-Command Multi-Container Deployment
```bash
# 1. Clone repository
git clone https://github.com/Ajaychaudhari09/Wellnexa.git
cd Wellnexa

# 2. Configure environment
cp .env.example .env

# 3. Spin up PostgreSQL 16 + pgvector and Backend
docker compose up -d

# 4. Run automated database migrations
cd backend
alembic upgrade head

# 5. Seed realistic demonstration data
python -m app.db.seed_demo_data
```

## 3. Web & Mobile Client Build
```bash
# Web Client Build
cd apps/mobile
flutter build web --release

# Android APK Build
flutter build apk --release
```

## 4. Production Security Checklist
- Set `ENVIRONMENT=production` and `DEBUG=false` in `.env`.
- Ensure `SECRET_KEY` is a 64-character cryptographically random string (`openssl rand -hex 32`).
- Enable SSL/TLS reverse proxy (Nginx / Cloudflare) with automated certbot renewal.
