"""
Async database session factory — SQLAlchemy 2.x with asyncpg.

Provides:
  - AsyncEngine and AsyncSession for all database operations
  - get_db() dependency for FastAPI route injection
  - Connection pooling with pre_ping for resilience (ADR risk R-4)
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

# Async engine with connection pool configuration
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,       # Validates connections before use (mitigates R-4)
    pool_recycle=3600,         # Recycle connections every hour
)

# Session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency — yields an async database session.
    Automatically commits on success, rolls back on exception.
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
