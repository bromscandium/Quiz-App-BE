from fastapi import HTTPException, status


class HealthCheckException(HTTPException):
    def __init__(
        self,
        service: str,
        message: str,
        status_code: int = status.HTTP_503_SERVICE_UNAVAILABLE,
    ):
        detail = {service: "health_check error", "message": message}
        super().__init__(status_code=status_code, detail=detail)
