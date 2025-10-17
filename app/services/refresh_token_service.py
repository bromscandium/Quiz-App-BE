from sqlite3 import IntegrityError
from uuid import UUID
from datetime import datetime, timezone

from app.exceptions.refresh_token_exceptions import (
    IntegrityErrorWithRefreshToken,
    NotFoundRefreshToken,
    InvalidRefreshToken,
)
from app.unit_of_work.uow import UnitOfWork
from app.utils import logger
from app.utils.refresh_token_util import RefreshTokenUtil


class RefreshTokenService:
    refresh_token_util: RefreshTokenUtil = RefreshTokenUtil()

    @classmethod
    async def create_refresh_token(cls, uow: UnitOfWork, user_id: UUID) -> str:
        try:
            token_hash = cls.refresh_token_util.generate_token_data()
            raw_token = token_hash.pop("raw_token")
            await uow.refresh_tokens.create(user_id=user_id, **token_hash)
            return raw_token
        except IntegrityError as e:
            logger.exception(f"DB integrity error while creating refresh token: {e}")
            raise IntegrityErrorWithRefreshToken
        except Exception as e:
            logger.exception(f"Unexpected error while creating refresh token: {e}")
            raise

    @classmethod
    async def verify_refresh_token(cls, uow: UnitOfWork, raw_token: str):
        try:
            hashed = cls.refresh_token_util.hash_token(raw_token)
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
        except Exception as e:
            logger.exception(f"Error verifying refresh token: {e}")
            raise

    @classmethod
    async def revoke_refresh_token(cls, uow: UnitOfWork, raw_token: str):
        try:
            token_obj = await cls.verify_refresh_token(uow, raw_token)
            if not token_obj:
                raise NotFoundRefreshToken
            await uow.refresh_tokens.update_by("id", token_obj.id, revoked=True)
        except NotFoundRefreshToken:
            raise
        except Exception as e:
            logger.exception(f"Error revoking refresh token: {e}")
            raise

    @classmethod
    async def rotate_refresh_token(
        cls, uow: UnitOfWork, old_raw_token: str, user_id: UUID
    ) -> str:
        try:
            old_token_obj = await cls.verify_refresh_token(uow, old_raw_token)
            if not old_token_obj or old_token_obj.user_id != user_id:
                raise InvalidRefreshToken
            await uow.refresh_tokens.update_by("id", old_token_obj.id, revoked=True)
            return await cls.create_refresh_token(uow, user_id)
        except InvalidRefreshToken:
            raise
        except Exception as e:
            logger.exception(f"Error rotating refresh token: {e}")
            raise

    @classmethod
    async def delete_refresh_token(cls, uow: UnitOfWork, user_id: UUID) -> None:
        try:
            tokens, _ = await uow.refresh_tokens.read("user_id", user_id)
            for token_obj in tokens:
                await uow.refresh_tokens.delete_by("id", token_obj.id)
        except Exception as e:
            logger.exception(f"Error deleting refresh tokens: {e}")
            raise
