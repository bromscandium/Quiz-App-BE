from typing import Type, TypeVar
from uuid import UUID

from pydantic import BaseModel

from app.db.redis import RedisClient

T = TypeVar("T", bound=BaseModel)


class RedisUtil:
    def __init__(self):
        self.redis = RedisClient()

    async def save(self, obj: T, prefix: str, ttl_hours: int = 48):
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

    async def read(
        self,
        object_id: UUID,
        schema: Type[T],
        prefix: str,
    ) -> T | None:
        redis_key = f"{prefix}:{object_id}"
        data = await self.redis.get_key(redis_key)

        if not data:
            return None

        return schema.model_validate_json(data.encode())

    async def read_by_prefix(self, prefix: str, schema: Type[T]) -> list[T]:
        keys = await self.redis.get_keys_by_pattern(f"{prefix}:*")
        cached_items: list[T] = []

        for key in keys:
            cached = await self.redis.get_key(key)
            if cached:
                cached_items.append(schema.model_validate_json(cached.encode()))

        if not cached_items:
            return []

        return cached_items
