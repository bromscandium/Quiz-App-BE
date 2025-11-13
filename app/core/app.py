from pydantic import Field
from pydantic_settings import SettingsConfigDict

from app.core import BaseConfig


class DbSettings(BaseConfig):
    user: str
    password: str
    host: str
    port: int
    db: str
    debug: bool = False

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"

    model_config = SettingsConfigDict(
        env_prefix="POSTGRES_",
    )


class RedisSettings(BaseConfig):
    host: str
    port: int

    @property
    def url(self) -> str:
        return f"rediss://{self.host}:{self.port}"

    model_config = SettingsConfigDict(
        env_prefix="REDIS_",
    )


class AppSettings(BaseConfig):
    host: str = Field(alias="HOST")
    port: int = Field(alias="PORT")
    mode: str = Field(alias="MODE")
    allowed_origins: list[str] = Field(default=["*"], alias="ALLOWED_ORIGINS")

    db: DbSettings = Field(default_factory=DbSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)

    model_config = SettingsConfigDict(
        populate_by_name=True,
    )


app_settings = AppSettings()
