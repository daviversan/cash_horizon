"""Database configuration and session management."""

from typing import AsyncGenerator
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from .config import settings

# Create declarative base for models
Base = declarative_base()

# Convert SQLite URL to async format if needed
database_url = settings.database_url
if database_url.startswith("sqlite:///"):
    # Convert to async SQLite URL
    async_database_url = database_url.replace("sqlite:///", "sqlite+aiosqlite:///")
else:
    async_database_url = database_url

# Create async engine
engine = create_async_engine(
    async_database_url,
    echo=settings.environment == "development",
    future=True,
    connect_args={"check_same_thread": False} if "sqlite" in async_database_url else {},
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Synchronous engine for migrations and seed data
sync_database_url = settings.database_url
sync_engine = create_engine(
    sync_database_url,
    echo=settings.environment == "development",
    connect_args={"check_same_thread": False} if "sqlite" in sync_database_url else {},
)

# Synchronous session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_sync_db() -> Session:
    """Get synchronous database session for migrations and scripts."""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()


async def init_db() -> None:
    """Initialize database tables."""
    async with engine.begin() as conn:
        # Import all models here to ensure they are registered
        from .models import company, transaction, agent_session  # noqa: F401
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()

