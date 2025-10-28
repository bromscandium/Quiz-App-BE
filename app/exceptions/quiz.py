from fastapi import HTTPException, status


class QuizNotFound(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, detail="Quiz was not found"
        )


class UnauthorizedQuizAction(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only company owner or administrator can perform this action",
        )


class InvalidQuizStructure(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid quiz structure"
        )
