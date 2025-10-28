from typing import TypeVar, Type
from uuid import UUID

from pydantic import BaseModel

from app.utils.logger import logger
from app.db.redis import RedisClient

T = TypeVar("T", bound=BaseModel)


class RedisUtil:
    def __init__(self):
        self.redis = RedisClient()

    async def save(self, obj: T, prefix: str, ttl_hours: int = 48):
        try:
            cursor = b"0"
            while cursor:
                cursor, keys = await self.redis.scan(
                    cursor=cursor, match=f"{prefix}:*", count=100
                )
                for key in keys:
                    await self.redis.expire(key, ttl_hours)
                if cursor == b"0":
                    break

            redis_key = f"{prefix}:{obj.id}"
            data = obj.model_dump_json()
            await self.redis.set_key(redis_key, data, expire_hours=ttl_hours)
        except Exception as e:
            logger.exception(f"Failed to save to Redis: {e}")

    async def read(
        self,
        object_id: UUID,
        schema: Type[T],
        prefix: str,
    ) -> T | None:
        try:
            redis_key = f"{prefix}:{object_id}"
            data = await self.redis.get_key(redis_key)

            if not data:
                return None

            return schema.model_validate_json(data.encode())
        except Exception as e:
            logger.exception(f"Failed to read from Redis: {e}")
            return None

    async def read_by_prefix(self, prefix: str, schema: Type[T]) -> list[T]:
        try:
            keys = await self.redis.get_keys_by_pattern(f"{prefix}:*")
            cached_items: list[T] = []

            for key in keys:
                cached = await self.redis.get_key(key)
                if cached:
                    cached_items.append(schema.model_validate_json(cached.encode()))

            if not cached_items:
                return []

            return cached_items
        except Exception as e:
            logger.exception(f"Failed to read list from Redis: {e}")
            return []
