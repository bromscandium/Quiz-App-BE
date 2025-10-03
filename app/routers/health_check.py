from fastapi import APIRouter, status, HTTPException
from sqlalchemy import text

from app.schemas.health_check import HealthCheckResponse
from app.db.postgres import sessionmanager
from app.db.redis import RedisClient

router = APIRouter()


@router.get(
    "/",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Basic health check",
    description="Returns basic health status of the application.",
)
async def health_check() -> HealthCheckResponse:
    return HealthCheckResponse(
        status_code=status.HTTP_200_OK, detail="ok", result="working"
    )


@router.get(
    "/db",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Database health check",
    description="Checks PostgreSQL database connectivity.",
)
async def health_check_db() -> HealthCheckResponse:
    try:
        async for session in sessionmanager.get_session():
            await session.execute(text("SELECT 1"))
        return HealthCheckResponse(
            status_code=status.HTTP_200_OK, detail="ok", result="working", database="ok"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"database": "error", "message": str(e)},
        )


@router.get(
    "/redis",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Redis health check",
    description="Checks Redis connectivity.",
)
async def health_check_redis() -> HealthCheckResponse:
    try:
        await RedisClient.redis_client.ping()
        return HealthCheckResponse(
            status_code=status.HTTP_200_OK, detail="ok", result="working", redis="ok"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"redis": "error", "message": str(e)},
        )
