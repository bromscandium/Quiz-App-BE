from uuid import UUID

from app.enums import Roles, NotificationStatuses
from app.exceptions import (
    InvalidQuizStructure,
    QuizNotFound,
    UnauthorizedQuizAction,
)
from app.schemas.notification import NotificationCreate
from app.schemas.question import QuestionsListCreate
from app.schemas.quiz import QuizCreate, QuizList, QuizSchema, QuizUpdate
from app.services.notification import NotificationService
from app.unit_of_work import UnitOfWork
from app.utils import LoggerUtil


class QuizService:
    def __init__(self):
        self.logger_util = LoggerUtil()
        self.notification_service = NotificationService()

    async def _check_user_permissions(
        self, uow: UnitOfWork, company_id: UUID, user_id: UUID
    ) -> None:
        memberships, _ = await uow.membership.read(
            field="user_id", value=user_id, offset=0, limit=100
        )

        if any(
            m.company_id == company_id
            and m.role in {Roles.ADMIN, Roles.OWNER}
            and m.is_active
            for m in memberships
        ):
            return

        self.logger_util.info("Unauthorized user")
        raise UnauthorizedQuizAction

    async def _get_quiz_by_id(self, uow, quiz_id: UUID) -> QuizSchema | None:
        quiz_with_question, _ = await uow.quizzes.read(
            field="id",
            value=quiz_id,
            offset=0,
            limit=1,
            load_relationships=["questions", "company", "questions.answer_options"],
        )

        if not quiz_with_question:
            return None

        return quiz_with_question[0]

    async def create_quiz(
        self,
        uow: UnitOfWork,
        data: QuizCreate,
        questions_data: QuestionsListCreate,
        current_user_id: UUID,
    ) -> QuizSchema:
        await self._check_user_permissions(uow, data.company_id, current_user_id)

        if len(questions_data.questions) < 2:
            self.logger_util.info("Not enough questions")
            raise InvalidQuizStructure

        questions = questions_data.questions

        for question in questions:
            if not question.title:
                self.logger_util.info("Question title is required")
                raise InvalidQuizStructure

            options = question.answer_options
            if not (2 <= len(options) <= 4):
                self.logger_util.info("Invalid number of options")
                raise InvalidQuizStructure
            if not any(o.is_correct for o in options):
                self.logger_util.info("Invalid options")
                raise InvalidQuizStructure

        quiz = await uow.quizzes.create(**data.model_dump())
        await uow.session.flush()

        for question in questions:
            q = await uow.questions.create(quiz_id=quiz.id, title=question.title)
            await uow.session.flush()
            for opt in question.answer_options:
                await uow.answer_options.create(
                    question_id=q.id, text=opt.text, is_correct=opt.is_correct
                )
                await uow.session.flush()

        quiz_with_question = await self._get_quiz_by_id(uow, quiz.id)

        memberships, total = await uow.membership.read(
            field="company_id",
            value=data.company_id,
            offset=0,
            limit=100,
            load_relationships=["user"],
        )
        active_members = [m for m in memberships if m.is_active]

        notification = await self.notification_service.create_notification(
            uow,
            data=NotificationCreate(
                message=f"New test {data.title} in your company",
                company_id=data.company_id,
            ),
        )

        await uow.session.flush()

        for member in active_members:
            await uow.user_notifications.create(
                user_id=member.user_id,
                notification_id=notification.id,
                status=NotificationStatuses.UNREAD,
            )

        return QuizSchema.model_validate(quiz_with_question)

    async def read_quiz_by_id(
        self, uow: UnitOfWork, quiz_id: UUID, current_user_id: UUID
    ) -> QuizSchema | None:
        quiz = await self._get_quiz_by_id(uow, quiz_id)

        memberships, _ = await uow.membership.read(
            field="user_id", value=current_user_id, offset=0, limit=100
        )

        active_membership = [
            m for m in memberships if m.company_id == quiz.company.id and m.is_active
        ]
        if not active_membership:
            self.logger_util.info("No active membership")
            raise UnauthorizedQuizAction

        return QuizSchema.model_validate(quiz)

    async def read_company_quizzes(
        self, uow: UnitOfWork, company_id: UUID, offset: int = 0, limit: int = 20
    ) -> QuizList:
        items, total = await uow.quizzes.read(
            field="company_id",
            value=company_id,
            offset=offset,
            limit=limit,
            load_relationships=["questions", "company", "questions.answer_options"],
        )

        quiz_schemas = [QuizSchema.model_validate(quiz) for quiz in items]
        return QuizList(quizzes=quiz_schemas, total=total)

    async def update_quiz(
        self,
        uow: UnitOfWork,
        quiz_id: UUID,
        data: QuizUpdate,
        current_user_id: UUID,
    ) -> QuizSchema:
        quiz = await self.read_quiz_by_id(uow, quiz_id, current_user_id)
        await self._check_user_permissions(uow, quiz.company_id, current_user_id)

        update_data = data.model_dump(exclude={"questions"}, exclude_unset=True)
        if update_data:
            await uow.quizzes.update_by("id", quiz_id, **update_data)
            await uow.session.flush()

        for question in data.questions:
            if question.id:
                new_question = await uow.questions.update_by(
                    "id", question.id, title=question.title
                )
            else:
                new_question = await uow.questions.create(
                    quiz_id=quiz_id, title=question.title
                )
                await uow.session.flush()

            for option in question.answer_options:
                if option.id:
                    await uow.answer_options.update_by(
                        "id", option.id, **option.model_dump(exclude_unset=True)
                    )
                else:
                    await uow.answer_options.create(
                        question_id=new_question.id,
                        **option.model_dump(exclude_unset=True),
                    )
                    await uow.session.flush()

        quiz_with_questions, _ = await uow.quizzes.read(
            field="id",
            value=quiz_id,
            offset=0,
            limit=1,
            load_relationships=["questions", "company", "questions.answer_options"],
        )

        return QuizSchema.model_validate(quiz_with_questions[0])

    async def delete_quiz(
        self, uow: UnitOfWork, quiz_id: UUID, current_user_id: UUID
    ) -> None:
        quiz = await self._get_quiz_by_id(uow, quiz_id)
        if quiz is None:
            self.logger_util.info("Quiz not found")
            raise QuizNotFound
        await self._check_user_permissions(uow, quiz.company_id, current_user_id)

        await uow.quizzes.delete_by("id", quiz_id)
