from datetime import timedelta

import redis.asyncio as redis

from app.core.app import app_settings
from app.utils import LoggerUtil


class RedisClient:
    logger_util: LoggerUtil = LoggerUtil()
    redis_client: redis.Redis = None

    @classmethod
    async def connect(cls):
        cls.redis_client = redis.from_url(app_settings.redis.url, decode_responses=True)
        cls.logger_util.info("Connecting to Redis...")
        try:
            await cls.redis_client.ping()
            cls.logger_util.info("Connected to Redis")
        except redis.RedisError as e:
            cls.logger_util.exception("Failed connection to Redis")
            raise

    @classmethod
    async def close(cls):
        if cls.redis_client:
            await cls.redis_client.aclose()
            cls.logger_util.info("Redis closed")

    @classmethod
    async def set_key(cls, key: str, value: str, expire_hours: int | None = None):
        if expire_hours:
            await cls.redis_client.setex(key, timedelta(hours=expire_hours), value)
        else:
            await cls.redis_client.set(key, value)

    @classmethod
    async def get_key(cls, key: str):
        return await cls.redis_client.get(key)

    @classmethod
    async def delete_key(cls, key: str):
        await cls.redis_client.delete(key)

    @classmethod
    async def get_keys_by_pattern(cls, pattern: str):
        return await cls.redis_client.keys(pattern)

    @classmethod
    async def scan(cls, cursor=0, match=None, count=None):
        return await cls.redis_client.scan(cursor=cursor, match=match, count=count)

    @classmethod
    async def expire(cls, key, ttl_hours):
        await cls.redis_client.expire(key, ttl_hours * 3600)
