from fastapi import HTTPException, status


class InvalidCredentialsException(HTTPException):
    def __init__(
        self,
        detail: str = "Invalid email or password",
        status_code: int = status.HTTP_401_UNAUTHORIZED,
    ):
        super().__init__(status_code=status_code, detail=detail)


class InvalidRefreshTokenWhileGenerating(HTTPException):
    def __init__(
        self,
        detail: str = "Invalid refresh token",
        status_code: int = status.HTTP_401_UNAUTHORIZED,
    ):
        super().__init__(status_code=status_code, detail=detail)


class InvalidTokenType(HTTPException):
    def __init__(
        self,
        detail: str = "Invalid token type",
        status_code: int = status.HTTP_401_UNAUTHORIZED,
    ):
        super().__init__(status_code=status_code, detail=detail)


class AuthError(HTTPException):
    def __init__(
        self,
        detail: str = "Authentication error",
        status_code: int = status.HTTP_401_UNAUTHORIZED,
    ):
        super().__init__(status_code=status_code, detail=detail)


class InvalidTokenFormat(AuthError):
    def __init__(self):
        super().__init__(detail="Invalid token format")


class Auth0UserFetchFailed(AuthError):
    def __init__(self):
        super().__init__(detail="Failed to fetch user info from Auth0")
