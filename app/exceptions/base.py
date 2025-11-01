from fastapi import status, HTTPException


class BadRequestErrorException(HTTPException):
    def __init__(self):
        super().__init__(
            detail="Bad request error",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class InternalServerErrorException(HTTPException):
    def __init__(self):
        super().__init__(
            detail="Internal server error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
