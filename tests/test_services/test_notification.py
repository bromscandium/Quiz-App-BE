from uuid import uuid4

from app.enums import NotificationStatuses
from tests.factories.notification import NotificationCreateFactory
from tests.factories.user_notification import UserNotificationUpdateFactory
from tests.fixtures import *


@pytest.fixture()
async def create_new_notification(uow, notification_service, company_1, user_1):
    notification_data = NotificationCreateFactory.build(company_id=company_1.id)
    notification = await notification_service.create_notification(
        uow, notification_data
    )

    user_notification = await uow.user_notifications.create(
        user_id=user_1.id,
        notification_id=notification.id,
        status=NotificationStatuses.UNREAD,
    )
    await uow.session.flush()
    await uow.session.refresh(user_notification)

    return notification


@pytest.mark.asyncio
async def test_create_notification(uow, notification_service, company_1):
    notification_data = NotificationCreateFactory.build(company_id=company_1.id)
    notification = await notification_service.create_notification(
        uow, notification_data
    )
    assert notification.id is not None
    assert notification.message == notification_data.message


@pytest.mark.asyncio
async def test_read_notification_by_id(uow, notification_service, user_1, company_1):
    notification_data = NotificationCreateFactory.build(company_id=company_1.id)
    notification = await notification_service.create_notification(
        uow, notification_data
    )

    read_notification = await notification_service.read_notification_by_id(
        uow, notification.id
    )

    assert read_notification.id == notification.id
    assert read_notification.message == notification_data.message


@pytest.mark.asyncio
async def test_non_existent_read_notification(uow, notification_service):
    non_existent_id = uuid4()
    assert (
        await notification_service.read_notification_by_id(uow, non_existent_id) is None
    )


@pytest.mark.asyncio
async def test_read_user_notifications(
    uow, notification_service, user_1, create_new_notification
):
    result = await notification_service.read_user_notifications(
        uow, user_1.id, user_1.id
    )
    assert result.total == 1
    assert result.notifications[0].notification_id == create_new_notification.id


@pytest.mark.asyncio
async def test_update_notification(
    uow, notification_service, create_new_notification, user_1
):
    updated_data = UserNotificationUpdateFactory.build(
        user_id=user_1.id,
        notification_id=create_new_notification.id,
        status=NotificationStatuses.READ,
    )

    updated = await notification_service.update_notification(
        uow, user_1.id, updated_data
    )
    assert updated.status == NotificationStatuses.READ


@pytest.mark.asyncio
async def test_delete_notification(
    uow, notification_service, user_1, create_new_notification
):
    deleted = await notification_service.delete_notification(
        uow, user_1.id, user_1.id, create_new_notification.id
    )
    assert deleted is None
