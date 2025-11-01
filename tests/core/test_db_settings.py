from pathlib import Path

from pydantic_settings import SettingsConfigDict

from app.core.base import BaseConfig


class DbSettings(BaseConfig):
    user: str
    password: str
    host: str
    port: int
    db: str

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"

    model_config = SettingsConfigDict(
        env_prefix="TEST_POSTGRES_",
        env_file=Path(__file__).parent.parent.parent / ".env.test",
        env_file_encoding="utf-8",
        populate_by_name=True,
    )
