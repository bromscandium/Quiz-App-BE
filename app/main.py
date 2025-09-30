from fastapi import FastAPI
from app.core.config import settings
import uvicorn

from app.schemas.health_check import HealthCheckResponse

app = FastAPI()


@app.get("/", response_model=HealthCheckResponse)
async def health_check() -> HealthCheckResponse:
    return HealthCheckResponse()


def start():
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=True)
