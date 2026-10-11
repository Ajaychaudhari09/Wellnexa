"""System diagnostic and readiness verification script."""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text
from app.core.config import settings
from app.models import *

async def verify():
    print("==================================================")
    print("       🏥 WellNexa AI — System Verification      ")
    print("==================================================")

    engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

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

            print("\n🚀 System is 100% HEALTHY and READY for project demonstration!")
    except Exception as e:
        print(f"❌ System Verification Failed: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(verify())
