from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.app import app_settings

engine = create_async_engine(
    app_settings.db.url,
    echo=app_settings.db.debug,
    pool_pre_ping=True,
    pool_recycle=app_settings.db.pool_recycle,
)

async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
