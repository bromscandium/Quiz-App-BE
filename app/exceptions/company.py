from fastapi import HTTPException, status


class CompanyException(HTTPException):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class CompanyNotFound(CompanyException):
    def __init__(self):
        super().__init__(
            detail="Company not found", status_code=status.HTTP_404_NOT_FOUND
        )


class InvitationNotFound(CompanyException):
    def __init__(self):
        super().__init__(
            detail="Invitation not found", status_code=status.HTTP_404_NOT_FOUND
        )


class NotOwnerOfCompany(CompanyException):
    def __init__(self):
        super().__init__(
            detail="Not Owner of Company", status_code=status.HTTP_403_FORBIDDEN
        )
