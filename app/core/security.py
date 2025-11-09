from pydantic import Field
from pydantic_settings import SettingsConfigDict

from app.core import BaseConfig


class JWTConfig(BaseConfig):
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int
    raw_token_bytes: int
    public_key_path: str
    private_key_path: str

    model_config = SettingsConfigDict(
        env_prefix="JWT_",
    )


class Auth0Config(BaseConfig):
    domain: str
    api_audience: str

    model_config = SettingsConfigDict(
        env_prefix="AUTH0_",
    )


class SecuritySettings(BaseConfig):
    jwt: JWTConfig = Field(default_factory=JWTConfig)
    auth0: Auth0Config = Field(default_factory=Auth0Config)

    model_config = SettingsConfigDict(
        populate_by_name=True,
    )


security_settings = SecuritySettings()
