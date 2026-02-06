from fastapi import HTTPException, status


class QuizAttemptNotFound(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, detail="Quiz attempt not found"
        )


class InvalidQuizAttempt(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid quiz attempt"
        )


class UnauthorizedQuizAttempt(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized manipulation with quiz attempt",
        )


class QuizNotAccessible(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN, detail="Quiz not accessible"
        )
