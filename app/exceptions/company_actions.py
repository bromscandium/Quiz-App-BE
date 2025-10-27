from fastapi import HTTPException, status


class CompanyActionsException(HTTPException):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class NotFoundActionType(CompanyActionsException):
    def __init__(self):
        super().__init__(
            detail="Not found Action Type", status_code=status.HTTP_404_NOT_FOUND
        )


class CompanyActionNotFound(CompanyActionsException):
    def __init__(self):
        super().__init__(
            detail="Company action not found", status_code=status.HTTP_404_NOT_FOUND
        )


class NotAllowedChangeCompanyAction(CompanyActionsException):
    def __init__(self):
        super().__init__(
            detail="Can't change company action, if it is not pending",
            status_code=status.HTTP_403_FORBIDDEN,
        )


class NotProvidedInfoForInvitation(CompanyActionsException):
    def __init__(self):
        super().__init__(
            detail="Not provided information for sending company action",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class PrivateCompany(CompanyActionsException):
    def __init__(self):
        super().__init__(
            detail="Error while sending request to private company",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
