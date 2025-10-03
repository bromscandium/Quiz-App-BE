from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_async_engine(
    settings.db.url,
    echo=settings.db.debug,
    pool_pre_ping=True,
    pool_recycle=settings.db.pool_recycle,
)

async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
