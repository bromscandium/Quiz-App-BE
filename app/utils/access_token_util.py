from datetime import datetime, timedelta, timezone
from pathlib import Path
import jwt

from app.core.security import security_settings


class AccessTokenUtil:
    def __init__(self):
        self.secret_key = security_settings.jwt.secret_key
        self.algorithm = security_settings.jwt.algorithm
        self.access_expire_minutes = security_settings.jwt.access_token_expire_minutes
        self.priv_path = Path(security_settings.jwt.private_key_path)
        self.pub_path = Path(security_settings.jwt.public_key_path)
        self.private_key: str | None = (
            self.priv_path.read_text() if self.priv_path.exists() else None
        )
        self.public_key: str | None = (
            self.pub_path.read_text() if self.pub_path.exists() else None
        )

    def _create_token(self, subject: str, delta: timedelta) -> str:
        now = datetime.now(timezone.utc)
        expire = now + delta
        payload = {
            "sub": str(subject),
            "iat": int(now.timestamp()),
            "exp": int(expire.timestamp()),
            "type": "access",
        }
        return jwt.encode(payload, self.private_key, algorithm=self.algorithm)

    def create_access_token(
        self, subject: str, expires_minutes: int | None = None
    ) -> str:
        delta = timedelta(minutes=expires_minutes or self.access_expire_minutes)
        return self._create_token(subject, delta)

    def decode_token(self, token: str) -> dict:
        return jwt.decode(token, self.public_key, algorithms=[self.algorithm])
