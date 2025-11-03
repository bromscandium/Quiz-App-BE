from fastapi import status, HTTPException


class InvalidTokenFormat(HTTPException):
    def __init__(self):
        super().__init__(detail="Invalid token format")


class Auth0Failed(HTTPException):
    def __init__(self):
        super().__init__(
            detail="Failed to fetch user info from Auth0 method",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class AuthFailed(HTTPException):
    def __init__(self):
        super().__init__(
            detail="Failed to fetch user info", status_code=status.HTTP_401_UNAUTHORIZED
        )


class InvalidEmail(HTTPException):
    def __init__(self):
        super().__init__(
            detail="Invalid email", status_code=status.HTTP_401_UNAUTHORIZED
        )


class InvalidPassword(HTTPException):
    def __init__(self):
        super().__init__(
            detail="Invalid password", status_code=status.HTTP_401_UNAUTHORIZED
        )
