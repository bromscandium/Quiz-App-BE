from fastapi import HTTPException, status


class InvitationException(HTTPException):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class InvitationInternalErrorException(InvitationException):
    def __init__(self, detail: str = "Internal server error"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class InvitationNotFound(InvitationException):
    def __init__(self, detail: str = "Not found invitation"):
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)


class NotProvidedInfoForInvitation(InvitationException):
    def __init__(self, detail: str = "Not enough information for sending invitation"):
        super().__init__(
            detail=detail,
        )
