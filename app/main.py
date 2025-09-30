from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
import uvicorn

from app.routers.root import router as root_router

app = FastAPI(title="Quiz App Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # In the future there will be specific origins, for dev purposes we accept everything
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(root_router, tags=["root"])


def start():
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=True)
