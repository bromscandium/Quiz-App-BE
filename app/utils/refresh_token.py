import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.core.security import security_settings
from app.exceptions.refresh_token import InvalidRefreshToken
from app.unit_of_work.uow import UnitOfWork


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

    async def create_refresh_token(self, uow: UnitOfWork, user_id: UUID) -> str:
        try:
            token_hash = self.generate_token_data()
            raw_token = token_hash.pop("raw_token")
            await uow.refresh_tokens.create(user_id=user_id, **token_hash)
            return raw_token
        except Exception:
            raise

    async def verify_refresh_token(self, uow: UnitOfWork, raw_token: str):
        try:
            hashed = self.hash_token(raw_token)
            items, _ = await uow.refresh_tokens.read(
                "token_hash", hashed, offset=0, limit=1
            )
            token_obj = items[0] if items else None
            if (
                not token_obj
                or token_obj.revoked
                or token_obj.expires_at < datetime.now(timezone.utc)
            ):
                return None
            return token_obj
        except Exception:
            raise

    async def rotate_refresh_token(
        self, uow: UnitOfWork, old_raw_token: str, user_id: UUID
    ) -> str:
        try:
            old_token_obj = await self.verify_refresh_token(uow, old_raw_token)
            if not old_token_obj or old_token_obj.user_id != user_id:
                raise InvalidRefreshToken
            await uow.refresh_tokens.update_by("id", old_token_obj.id, revoked=True)
            return await self.create_refresh_token(uow, user_id)
        except InvalidRefreshToken:
            raise
        except Exception:
            raise

    async def delete_refresh_token(self, uow: UnitOfWork, user_id: UUID) -> None:
        try:
            tokens, _ = await uow.refresh_tokens.read("user_id", user_id)
            for token_obj in tokens:
                await uow.refresh_tokens.delete_by("id", token_obj.id)
        except Exception:
            raise
