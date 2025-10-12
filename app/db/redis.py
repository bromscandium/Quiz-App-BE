import redis.asyncio as redis

from app.utils import logger
from app.core.config import settings


class RedisClient:
    redis_client: redis.Redis = None

    @classmethod
    async def connect(cls):
        cls.redis_client = redis.from_url(settings.redis.url, decode_responses=True)
        logger.info("Connecting to Redis...")
        try:
            await cls.redis_client.ping()
            logger.info("Connected to Redis")
        except redis.RedisError as e:
            logger.exception("Failed connection to Redis")
            raise

    @classmethod
    async def close(cls):
        if cls.redis_client:
            await cls.redis_client.aclose()
            logger.info("Redis closed")

    @classmethod
    async def set_key(cls, key: str, value: str):
        await cls.redis_client.set(key, value)

    @classmethod
    async def get_key(cls, key: str):
        return await cls.redis_client.get(key)
