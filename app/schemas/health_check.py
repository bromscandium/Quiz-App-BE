from pydantic import BaseModel


class HealthCheckResponse(BaseModel):
    status_code: int = 200
    detail: str = "ok"
    result: str = "working"
