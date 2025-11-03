from fastapi import status, HTTPException


class UserAlreadyExists(HTTPException):
    def __init__(self):
        super().__init__(
            detail="User already exists",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class UnauthorizedUserAction(HTTPException):
    def __init__(self):
        super().__init__(
            detail="Unauthorized user access",
            status_code=status.HTTP_403_FORBIDDEN,
        )


class UserNotFound(HTTPException):
    def __init__(self):
        super().__init__(
            detail="User not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
