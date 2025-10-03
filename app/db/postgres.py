from __future__ import annotations
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import AsyncAdaptedQueuePool

from app.core.config import settings


class SessionManager:
    def __init__(self) -> None:
        self.engine: Optional[AsyncEngine] = None
        self.session_factory: Optional[async_sessionmaker[AsyncSession]] = None

    def init_db(self) -> None:
        self.engine = create_async_engine(
            settings.db.url,
            poolclass=AsyncAdaptedQueuePool,
            pool_size=settings.db.pool_size,
            max_overflow=settings.db.max_overflow,
            pool_pre_ping=True,
            pool_recycle=settings.db.pool_recycle,
            echo=settings.db.debug,
        )

        self.session_factory = async_sessionmaker(
            self.engine,
            expire_on_commit=False,
            autoflush=False,
            class_=AsyncSession,
        )

    async def close(self) -> None:
        if self.engine:
            await self.engine.dispose()

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        if not self.session_factory:
            raise RuntimeError("Database session factory is not initialized.")

        async with self.session_factory() as session:
            try:
                yield session
            except Exception as e:
                await session.rollback()
                raise RuntimeError(f"Database session error: {e!r}") from e


sessionmanager = SessionManager()
Base = declarative_base()
