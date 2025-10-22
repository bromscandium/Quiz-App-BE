from fastapi import HTTPException, status


class CompanyException(HTTPException):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class CompanyNotFoundException(CompanyException):
    def __init__(self):
        super().__init__(
            detail="Company not found", status_code=status.HTTP_404_NOT_FOUND
        )


class CompanyInternalErrorException(CompanyException):
    def __init__(self, detail: str = "Internal server error"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
