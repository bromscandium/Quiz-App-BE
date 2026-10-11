from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.app import app_settings
from app.db.redis import RedisClient
from app.routers import routers
from app.utils import LoggerUtil


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = None
    try:
        await RedisClient.connect()
        redis_client = RedisClient
        app.state.redis = redis_client
        yield
    except Exception as e:
        raise e
    finally:
        if redis_client:
            await redis_client.close()


app = FastAPI(title="Quiz App Backend", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=app_settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in routers:
    app.include_router(router)


def start():
    uvicorn.run(
        "app.main:app", host=app_settings.host, port=app_settings.port, reload=True
    )
    logger = LoggerUtil()
    logger.info(msg="Server started")


if __name__ == "__main__":
    start()
