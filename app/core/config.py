from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    host: str
    port: int

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_prefix="QUIZAPP_"
    )


settings = Settings()
