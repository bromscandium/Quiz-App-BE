from fastapi import HTTPException, status


class RefreshTokenException(HTTPException):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class InvalidRefreshToken(RefreshTokenException):
    def __init__(self):
        super().__init__(detail="Invalid refresh token")


class IntegrityErrorWithRefreshToken(RefreshTokenException):
    def __init__(self):
        super().__init__(detail="DB integrity error while creating refresh token")


class NotFoundRefreshToken(RefreshTokenException):
    def __init__(self):
        super().__init__(
            detail="Refresh token not found", status_code=status.HTTP_404_NOT_FOUND
        )


class ExpiredRefreshToken(RefreshTokenException):
    def __init__(self):
        super().__init__(
            detail="Refresh token has expired", status_code=status.HTTP_401_UNAUTHORIZED
        )


class RevokedRefreshToken(RefreshTokenException):
    def __init__(self):
        super().__init__(
            detail="Refresh token has been revoked",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
