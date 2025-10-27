from fastapi import HTTPException, status
from starlette.status import HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN


class MembershipException(HTTPException):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class MembershipNotFound(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=HTTP_404_NOT_FOUND, detail="Membership was not found"
        )


class SetAnotherOwner(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=HTTP_403_FORBIDDEN,
            detail="Cannot exist two owners in one company",
        )
