from fastapi import status, HTTPException


class NotFoundActionType(HTTPException):
    def __init__(self):
        super().__init__(
            detail="Not found action type",
        )


class CompanyActionNotFound(HTTPException):
    def __init__(self):
        super().__init__(
            detail="Company action not found",
        )


class NotAllowedChangeCompanyAction(HTTPException):
    def __init__(self):
        super().__init__(
            detail="Can't change company action, if it is not pending",
            status_code=status.HTTP_403_FORBIDDEN,
        )


class NotProvidedInfoForCompanyAction(HTTPException):
    def __init__(self):
        super().__init__(
            detail="No provided information for sending company actio",
        )
