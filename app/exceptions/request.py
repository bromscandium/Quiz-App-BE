from fastapi import HTTPException, status


class RequestException(HTTPException):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class RequestInternalErrorException(RequestException):
    def __init__(self, detail: str = "Internal server error"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class RequestNotFound(RequestException):
    def __init__(self, detail: str = "Not found request"):
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)


class NotProvidedInfoForRequest(RequestException):
    def __init__(self, detail: str = "Not enough information for sending request"):
        super().__init__(
            detail=detail,
        )


class PrivateCompanyExceptionForRequest(RequestException):
    def __init__(self, detail: str = "Company is private"):
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN)


class UnauthorizedRequestException(RequestException):
    def __init__(self):
        super().__init__(
            detail="Unauthorized Request to Company",
            status_code=status.HTTP_403_FORBIDDEN,
        )
