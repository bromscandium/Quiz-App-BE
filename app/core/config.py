from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DbSettings(BaseSettings):
    user: str
    password: str
    host: str
    port: int
    db: str
    url: str
    pool_size: int
    max_overflow: int
    pool_recycle: int
    debug: bool

    model_config = SettingsConfigDict(
        env_prefix="POSTGRES_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class RedisSettings(BaseSettings):
    host: str
    port: int
    url: str

    model_config = SettingsConfigDict(
        env_prefix="REDIS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class AppSettings(BaseSettings):
    host: str = Field(alias="HOST")
    port: int = Field(alias="PORT")
    mode: str = Field(alias="MODE")
    allowed_origins: List[str] = Field(default=["*"], alias="ALLOWED_ORIGINS")

    db: DbSettings = Field(default_factory=DbSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        populate_by_name=True,
        extra="ignore",
    )


settings = AppSettings()
