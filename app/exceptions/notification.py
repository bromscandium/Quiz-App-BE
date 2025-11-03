from fastapi import status, HTTPException


class NotificationNotFound(HTTPException):
    def __init__(self):
        super().__init__(
            detail="Notification not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
