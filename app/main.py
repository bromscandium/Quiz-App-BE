from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
import uvicorn

from app.schemas.health_check import HealthCheckResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # In the future there will be specific origins, for dev purposes we accept everything
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=HealthCheckResponse)
async def health_check() -> HealthCheckResponse:
    return HealthCheckResponse()


def start():
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=True)
