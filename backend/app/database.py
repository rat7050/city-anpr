from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator
from .config import settings
from sqlalchemy import text, event
import logging

logger = logging.getLogger(__name__)

# Determine if we're using SQLite (dev mode) or PostgreSQL (production)
is_sqlite = settings.DATABASE_URL.startswith("sqlite")

engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        if not is_sqlite:
            # Create PostGIS extension if not exists (PostgreSQL only)
            try:
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
            except Exception as e:
                logger.warning(f"Could not create PostGIS extension: {e}")
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    logger.info(f"Database initialized ({'SQLite dev mode' if is_sqlite else 'PostgreSQL'})")
