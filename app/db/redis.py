import redis.asyncio as redis
from app.core.config import settings


class RedisClient:
    redis_client: redis.Redis = None

    @classmethod
    async def connect(cls):
        cls.redis_client = redis.from_url(settings.redis.url, decode_responses=True)
        try:
            await cls.redis_client.ping()
            print("Redis connected")
        except redis.RedisError as e:
            print(f"Redis connection failed: {e}")
            raise

    @classmethod
    async def close(cls):
        if cls.redis_client:
            await cls.redis_client.aclose()
            print("Redis closed")

    @classmethod
    async def set_key(cls, key: str, value: str):
        await cls.redis_client.set(key, value)

    @classmethod
    async def get_key(cls, key: str):
        return await cls.redis_client.get(key)
