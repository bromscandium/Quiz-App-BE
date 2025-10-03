from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class HealthCheckResponse(BaseModel):
    status_code: int = Field(..., description="HTTP-like status code")
    detail: str = Field(..., description="Message about the request result")
    result: str = Field(..., description="Result from the server")
    database: Optional[str] = Field(None, description="Database connectivity status")
    redis: Optional[str] = Field(None, description="Redis connectivity status")
