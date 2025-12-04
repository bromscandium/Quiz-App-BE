from uuid import UUID

from fastapi import APIRouter, Depends
from starlette import status

from app.dependencies import get_uow, get_auth_user_from_cookie
from app.schemas.notification import NotificationCreate, NotificationSchema
from app.schemas.user_notification import (
    UserNotificationUpdate,
    UserNotificationsList,
    UserNotificationSchema,
)
from app.services.notification import NotificationService
from app.unit_of_work import UnitOfWork

router = APIRouter(prefix="/notifications", tags=["notifications"])
notification_service = NotificationService()


@router.post(
    "/", response_model=NotificationSchema, status_code=status.HTTP_201_CREATED
)
async def create_notification(
    data: NotificationCreate, uow: UnitOfWork = Depends(get_uow)
) -> NotificationSchema:
    return await notification_service.create_notification(uow, data)


@router.get(
    "/id/{notification_id}",
    response_model=NotificationSchema,
    status_code=status.HTTP_200_OK,
)
async def read_notification_by_id(
    notification_id: UUID, uow: UnitOfWork = Depends(get_uow)
) -> NotificationSchema | None:
    return await notification_service.read_notification_by_id(uow, notification_id)


@router.get(
    "/user/{user_id}/all",
    response_model=UserNotificationsList,
    status_code=status.HTTP_200_OK,
)
async def read_user_notifications(
    user_id: UUID,
    current_user_id: UUID = Depends(get_auth_user_from_cookie),
    offset: int = 0,
    limit: int = 20,
    uow: UnitOfWork = Depends(get_uow),
) -> UserNotificationsList:
    return await notification_service.read_user_notifications(
        uow, user_id, current_user_id, offset, limit
    )


@router.patch(
    "/update/{notification_id}",
    response_model=UserNotificationUpdate,
    status_code=status.HTTP_200_OK,
)
async def update_notification(
    data: UserNotificationUpdate,
    current_user_id: UUID = Depends(get_auth_user_from_cookie),
    uow: UnitOfWork = Depends(get_uow),
) -> UserNotificationSchema:
    return await notification_service.update_notification(uow, current_user_id, data)


@router.delete("/delete/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: UUID,
    user_id: UUID,
    current_user_id: UUID = Depends(get_auth_user_from_cookie),
    uow: UnitOfWork = Depends(get_uow),
) -> None:
    await notification_service.delete_notification(
        uow, current_user_id, user_id, notification_id
    )
