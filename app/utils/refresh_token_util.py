import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from app.core.security import security_settings


class RefreshTokenUtil:
    def __init__(self):
        self.default_expires_days = security_settings.jwt.refresh_token_expire_days
        self.raw_token_bytes = security_settings.jwt.raw_token_bytes

    def generate_token_data(self, expires_days: int | None = None) -> dict:
        raw_token = self.generate_raw_token()
        hashed_value = self.hash_token(raw_token)
        expires_at = self.get_expires_at(expires_days)

        return {
            "raw_token": raw_token,
            "token_hash": hashed_value,
            "expires_at": expires_at,
            "revoked": False,
        }

    def generate_raw_token(self) -> str:
        return secrets.token_urlsafe(self.raw_token_bytes)

    def hash_token(self, raw_token: str) -> str:
        return hashlib.sha512(raw_token.encode("utf-8")).hexdigest()

    def get_expires_at(self, expires_days: int | None = None) -> datetime:
        return datetime.now(timezone.utc) + timedelta(
            days=expires_days or self.default_expires_days
        )
