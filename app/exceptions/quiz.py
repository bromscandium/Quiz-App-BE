from fastapi import status, HTTPException


class UnauthorizedQuizAction(HTTPException):
    def __init__(self):
        super().__init__(
            detail="Only company owner or administrator can perform this action",
            status_code=status.HTTP_403_FORBIDDEN,
        )


class QuizNotFound(HTTPException):
    def __init__(self):
        super().__init__(
            detail="Quiz not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class InvalidQuizStructure(HTTPException):
    def __init__(self):
        super().__init__(
            detail="Invalid quiz structure",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
