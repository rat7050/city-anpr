from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator
from .config import settings
from sqlalchemy import text

engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        # Create PostGIS extension if not exists
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
