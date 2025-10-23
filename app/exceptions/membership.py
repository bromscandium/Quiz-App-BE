from fastapi import HTTPException, status
from starlette.status import HTTP_404_NOT_FOUND


class MembershipException(HTTPException):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class NoMembershipFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=HTTP_404_NOT_FOUND, detail="Membership was not found"
        )


class MembershipInternalErrorException(MembershipException):
    def __init__(self, detail: str = "Internal server error"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
