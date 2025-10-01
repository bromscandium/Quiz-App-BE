from fastapi import APIRouter, status
from app.schemas.root import RootResponse

router = APIRouter()


@router.get(
    "/",
    response_model=RootResponse,
    status_code=status.HTTP_200_OK,
    summary="Root endpoint",
    description="Returns basic root information.",
)
async def root() -> RootResponse:
    return RootResponse(status_code=status.HTTP_200_OK, detail="ok", result="working")
