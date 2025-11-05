from datetime import datetime, timedelta
import asyncio

from app.db.celery_worker import celery_app
from app.db.postgres import async_session
from app.enums import NotificationStatuses
from app.unit_of_work import UnitOfWork
from app.services.notification import NotificationService
from app.schemas.notification import NotificationCreate


@celery_app.task(name="app.tasks.quiz")
def check_quizzes():
    asyncio.run(_check_quizzes_async())


async def _check_quizzes_async():
    notification_service = NotificationService()

    async with UnitOfWork(async_session) as uow:
        offset = 0
        limit = 20

        while True:
            companies, _ = await uow.company.read(
                offset=offset, limit=limit, load_relationships=["owner"]
            )
            if not companies:
                break

            for company in companies:
                memberships, _ = await uow.membership.read(
                    field="company_id",
                    value=company.id,
                    offset=0,
                    limit=100,
                    load_relationships=["user", "company", "company.owner"],
                )

                quizzes, _ = await uow.quizzes.read(
                    field="company_id",
                    value=company.id,
                    offset=0,
                    limit=100,
                )
                for quiz in quizzes:
                    for membership in memberships:
                        user = membership.user

                        attempts, _ = await uow.quiz_attempts.read(
                            field="quiz_id", value=quiz.id, offset=0, limit=1000
                        )

                        user_attempts = [a for a in attempts if a.user_id == user.id]

                        if not user_attempts:
                            await _create_notification(
                                uow,
                                notification_service,
                                company.id,
                                user.id,
                                f"{user.nickname} hasn't completed the quiz '{quiz.title}' yet.",
                            )
                            continue

                        last_attempt = max(user_attempts, key=lambda a: a.created_at)

                        if last_attempt.created_at < (
                            datetime.now() - timedelta(hours=24)
                        ):
                            await _create_notification(
                                uow,
                                notification_service,
                                company.id,
                                user.id,
                                f"Reminder: {user.nickname} needs to retake the quiz '{quiz.title}'.",
                            )

            offset += limit


async def _create_notification(
    uow, notification_service, company_id, user_id, message: str
):
    notification = await notification_service.create_notification(
        uow=uow, data=NotificationCreate(company_id=company_id, message=message)
    )

    await uow.user_notifications.create(
        user_id=user_id,
        notification_id=notification.id,
        status=NotificationStatuses.UNREAD,
    )

    await uow.commit()
