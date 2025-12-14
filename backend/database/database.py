"""
Database Connection و Session Management
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from typing import AsyncGenerator

# Database URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/content_factory"
)

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # در Production باید False باشد
    future=True
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency برای دریافت Database Session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """ایجاد جداول Database"""
    from .models import Base
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

