from fastapi import HTTPException, status


class AuthException(HTTPException):
    def __init__(self, detail: str, status_code: int = status.HTTP_401_UNAUTHORIZED):
        super().__init__(status_code=status_code, detail=detail)


class InvalidCredentialsException(AuthException):
    def __init__(self):
        super().__init__(detail="Invalid email or password")


class InvalidRefreshTokenWhileGenerating(AuthException):
    def __init__(self):
        super().__init__(detail="Invalid refresh token")


class InvalidTokenType(AuthException):
    def __init__(self):
        super().__init__(detail="Invalid token type")


class AuthError(AuthException):
    def __init__(self):
        super().__init__(detail="Authentication error")


class InvalidTokenFormat(AuthException):
    def __init__(self):
        super().__init__(detail="Invalid token format")


class Auth0UserFetchFailed(AuthException):
    def __init__(self):
        super().__init__(detail="Failed to fetch user info from Auth0")


class InvalidTokenHeader(AuthException):
    def __init__(self):
        super().__init__(detail="Invalid token header")
