from fastapi import HTTPException, status


class UserException(HTTPException):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class UserNotFound(UserException):
    def __init__(self):
        super().__init__(
            detail="User not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class UserAlreadyExists(UserException):
    def __init__(self):
        super().__init__(
            detail="User already exists",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class UnauthorizedUserAction(UserException):
    def __init__(self):
        super().__init__(
            detail="Unathorized Access Of Manipulating User Data",
            status_code=status.HTTP_403_FORBIDDEN,
        )


class RequestNotFound(UserException):
    def __init__(self):
        super().__init__(
            detail="Invitation not found", status_code=status.HTTP_404_NOT_FOUND
        )
