"""System diagnostic and readiness verification script."""

import sys
import asyncio
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text

# Ensure backend directory is in sys.path
backend_path = Path(__file__).resolve().parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.core.config import settings
from app.models import *

async def verify():
    print("==================================================")
    print("       🏥 WellNexa AI — System Verification      ")
    print("==================================================")

    engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    success = False
    try:
        async with session_factory() as db:
            # Check database ping
            res = await db.execute(text("SELECT 1;"))
            ping = res.scalar()
            print(f"✅ Database Connection: ONLINE (Ping: {ping})")

            # Check users count
            users_res = await db.execute(text("SELECT count(*) FROM users;"))
            user_count = users_res.scalar()
            print(f"✅ Users Registered: {user_count}")

            # Check models registered
            table_count = len(Base.metadata.tables)
            print(f"✅ Schema Tables Registered: {table_count} tables")

            print("\n✅ Database and ORM checks passed.")
            print("ℹ️ SMTP delivery, OCR accuracy, AI provider access, and browser workflows are not checked by this script.")
            success = True
    except Exception as exc:
        # Database errors can include URLs, usernames, or query parameters.
        print(f"❌ System verification failed ({type(exc).__name__}). Check database configuration and schema.")
    finally:
        await engine.dispose()
    return success

if __name__ == "__main__":
    if not asyncio.run(verify()):
        raise SystemExit(1)
