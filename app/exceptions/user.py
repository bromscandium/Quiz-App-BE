from fastapi import HTTPException, status


class UserException(HTTPException):
    def __init__(
        self,
        detail: str = "User error",
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ):
        super().__init__(status_code=status_code, detail=detail)


class UserNotFoundException(UserException):
    def __init__(self):
        super().__init__(
            detail="User not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class UserAlreadyExistsException(UserException):
    def __init__(self):
        super().__init__(
            detail="User already exists",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class UnauthorizedUserActionException(UserException):
    def __init__(self):
        super().__init__(
            detail="Unathorized Access Of Manipulating User Data",
            status_code=status.HTTP_403_FORBIDDEN,
        )


class UserInternalErrorException(UserException):
    def __init__(self, detail: str = "Internal server error"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
