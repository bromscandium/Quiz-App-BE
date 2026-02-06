from pydantic import BaseModel, Field


class HealthCheckResponse(BaseModel):
    status_code: int = Field(..., description="HTTP-like status code")
    detail: str = Field(..., description="Message about the request result")
    result: str = Field(..., description="Result from the server")
    database: str | None = Field(None, description="Database connectivity status")
    redis: str | None = Field(None, description="Redis connectivity status")
