from fastapi import status, HTTPException


class MembershipNotFound(HTTPException):
    def __init__(self):
        super().__init__(
            detail="Membership not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class SetAnotherOwnerError(HTTPException):
    def __init__(self):
        super().__init__(
            detail="Cannot exist two owners in one company",
            status_code=status.HTTP_403_FORBIDDEN,
        )
