from fastapi import status, HTTPException


class UnauthorizedQuizAttempt(HTTPException):
    def __init__(self):
        super().__init__(
            detail="Unauthorized manipulation with quiz attempt",
            status_code=status.HTTP_403_FORBIDDEN,
        )


class InvalidQuizAttempt(HTTPException):
    def __init__(self):
        super().__init__(
            detail="Invalid quiz attempt",
            status_code=status.HTTP_403_FORBIDDEN,
        )
