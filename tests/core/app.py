from pydantic_settings import SettingsConfigDict
from tests.core.base import BaseConfig


class RedisSettings(BaseConfig):
    host: str

    @property
    def url(self) -> str:
        return f"redis://{self.host}:6379"

    model_config = SettingsConfigDict(
        env_prefix="TEST_REDIS_",
    )


class DbSettings(BaseConfig):
    user: str
    password: str
    host: str
    db: str

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:5432/{self.db}"

    model_config = SettingsConfigDict(
        env_prefix="TEST_POSTGRES_",
    )
