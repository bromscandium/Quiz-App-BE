from datetime import datetime, timedelta, timezone
from pathlib import Path

import jwt

from app.core.security import security_settings


class AuthTokenUtil:
    def __init__(self):
        self.secret_key = security_settings.jwt.secret_key
        self.algorithm = security_settings.jwt.algorithm
        self.access_expire_minutes = security_settings.jwt.access_token_expire_minutes
        self.refresh_expire_days = security_settings.jwt.refresh_token_expire_days
        self.priv_path = Path(security_settings.jwt.private_key_path)
        self.pub_path = Path(security_settings.jwt.public_key_path)
        self.private_key: str | None = (
            self.priv_path.read_text() if self.priv_path.exists() else None
        )
        self.public_key: str | None = (
            self.pub_path.read_text() if self.pub_path.exists() else None
        )

    def _create_token(
        self, subject: str, expire_delta: timedelta, token_type: str
    ) -> str:
        now = datetime.now(timezone.utc)
        expire = now + expire_delta
        payload = {
            "sub": str(subject),
            "iat": int(now.timestamp()),
            "exp": int(expire.timestamp()),
            "type": token_type,
        }
        return jwt.encode(payload, self.private_key, algorithm=self.algorithm)

    def create_tokens(self, subject: str) -> dict:
        access_token = self._create_token(
            subject, timedelta(minutes=self.access_expire_minutes), token_type="access"
        )
        refresh_token = self._create_token(
            subject, timedelta(days=self.refresh_expire_days), token_type="refresh"
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    def decode_token(self, token: str) -> dict:
        return jwt.decode(token, self.public_key, algorithms=[self.algorithm])

    def refresh_tokens(self, refresh_token: str) -> dict | None:
        try:
            data = self.decode_token(refresh_token)
            if data.get("type") != "refresh":
                return None
            subject = data.get("sub")
            return self.create_tokens(subject)
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return None
