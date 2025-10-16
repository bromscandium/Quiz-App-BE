from fastapi import HTTPException, status


class InvalidRefreshTokenException(HTTPException):
    def __init__(
        self,
        detail: str = "Invalid refresh token",
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ):
        super().__init__(status_code=status_code, detail=detail)


class IntegrityErrorWithRefreshToken(HTTPException):
    def __init__(
        self,
        detail: str = "DB integrity error while creating refresh token",
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ):
        super().__init__(status_code=status_code, detail=detail)


class NotFoundRefreshToken(HTTPException):
    def __init__(
        self,
        detail: str = "Refresh Token Not Found",
        status_code: int = status.HTTP_404_NOT_FOUND,
    ):
        super().__init__(status_code=status_code, detail=detail)
