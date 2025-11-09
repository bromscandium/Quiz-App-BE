from fastapi import status, HTTPException


class CompanyNotFound(HTTPException):
    def __init__(self):
        super().__init__(
            detail="Company not found", status_code=status.HTTP_404_NOT_FOUND
        )


class UnauthorizedCompanyOwner(HTTPException):
    def __init__(self):
        super().__init__(
            detail="Not owner of this company", status_code=status.HTTP_403_FORBIDDEN
        )


class PrivateCompany(HTTPException):
    def __init__(self):
        super().__init__(
            detail="Company is private", status_code=status.HTTP_403_FORBIDDEN
        )
