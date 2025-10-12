from fastapi import HTTPException, status


class UserException(HTTPException):
    def __init__(
        self, detail: str = "User error", status_code: int = status.HTTP_400_BAD_REQUEST
    ):
        super().__init__(status_code=status_code, detail=detail)


class UserNotFoundException(UserException):
    def __init__(self):
        super().__init__(
            detail=f"User not found", status_code=status.HTTP_404_NOT_FOUND
        )


class UserAlreadyExistsException(UserException):
    def __init__(self):
        super().__init__(
            detail=f"User already exists", status_code=status.HTTP_400_BAD_REQUEST
        )


class UserInternalErrorException(UserException):
    def __init__(self, message: str = "Internal server error"):
        super().__init__(
            detail=message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
