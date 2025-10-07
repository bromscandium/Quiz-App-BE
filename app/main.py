from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core import logger
from app.core.config import settings
from app.db.redis import RedisClient
from app.routers.health_check import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await RedisClient.connect()
        app.state.redis = RedisClient
        yield
    except Exception as e:
        raise
    finally:
        await app.state.redis.close()


app = FastAPI(title="Quiz App Backend", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, tags=["health"])


def start():
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=True)
    logger.info("Server started")


if __name__ == "__main__":
    start()
