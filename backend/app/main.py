from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.exceptions import WellNexaException
from app.core.security_headers import SecurityHeadersMiddleware
from app.modules.health.router import router as health_router
from app.modules.auth.router import router as auth_router
from app.modules.profile.router import router as profile_router
from app.modules.health.metrics_router import router as metrics_router
from app.modules.health.health_profile_router import router as health_profile_router
from app.modules.timeline.router import router as timeline_router
from app.modules.documents.router import router as documents_router
from app.modules.reports.router import router as reports_router
from app.modules.medicines.router import router as medicines_router
from app.modules.reminders.router import router as reminders_router
from app.modules.nutrition.router import router as nutrition_router
from app.modules.fitness.router import router as fitness_router
from app.modules.wellness.router import router as wellness_router
from app.modules.assistant.router import router as assistant_router
from app.modules.doctor.router import router as doctor_router
from app.modules.privacy.router import router as privacy_router
from app.modules.dashboard.router import router as dashboard_router
from app.modules.snapshot.router import router as snapshot_router
from app.modules.notifications.router import router as notifications_router
from app.modules.audit.router import router as audit_router
from app.modules.appointments.router import router as appointments_router

import sys
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifespan events."""
    print(f"[WellNexa AI] Initializing backend services in {settings.ENVIRONMENT} mode...")
    from app.core.database import engine, Base
    import app.models  # ensure models are loaded
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    from app.db.seed_demo_data import seed_all
    try:
        await seed_all()
    except Exception as e:
        print(f"Seed note: {e}")
    yield
    print("[WellNexa AI] Shutting down backend services...")

app = FastAPI(
    title=settings.APP_NAME,
    description="WellNexa AI — Cross-Platform Personal Healthcare and Wellness Management System API",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Security Headers & CORS Middleware configuration
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handlers
@app.exception_handler(WellNexaException)
async def wellnexa_exception_handler(request: Request, exc: WellNexaException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": exc.detail, "data": None, "errors": [str(exc.detail)]},
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"success": False, "message": "An internal server error occurred.", "data": None, "errors": [str(exc)]},
    )

# Include API Domain Routers
app.include_router(health_router, prefix=settings.API_V1_STR)
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(profile_router, prefix=settings.API_V1_STR)
app.include_router(metrics_router, prefix=settings.API_V1_STR)
app.include_router(health_profile_router, prefix=settings.API_V1_STR)
app.include_router(timeline_router, prefix=settings.API_V1_STR)
app.include_router(documents_router, prefix=settings.API_V1_STR)
app.include_router(reports_router, prefix=settings.API_V1_STR)
app.include_router(medicines_router, prefix=settings.API_V1_STR)
app.include_router(reminders_router, prefix=settings.API_V1_STR)
app.include_router(nutrition_router, prefix=settings.API_V1_STR)
app.include_router(fitness_router, prefix=settings.API_V1_STR)
app.include_router(wellness_router, prefix=settings.API_V1_STR)
app.include_router(assistant_router, prefix=settings.API_V1_STR)
app.include_router(doctor_router, prefix=settings.API_V1_STR)
app.include_router(privacy_router, prefix=settings.API_V1_STR)
app.include_router(dashboard_router, prefix=settings.API_V1_STR)
app.include_router(snapshot_router, prefix=settings.API_V1_STR)
app.include_router(notifications_router, prefix=settings.API_V1_STR)
app.include_router(audit_router, prefix=settings.API_V1_STR)
app.include_router(appointments_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": "0.1.0",
        "status": "online",
        "docs": "/docs",
        "health": f"{settings.API_V1_STR}/health",
    }
