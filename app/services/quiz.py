from uuid import UUID

from app.exceptions.base import InternalErrorException
from app.unit_of_work.uow import UnitOfWork
from app.schemas.quiz import QuizSchema, QuizCreate, QuizUpdate, QuizList
from app.schemas.question import QuestionsListCreate
from app.utils.logger import logger
from app.exceptions.quiz import (
    QuizNotFound,
    UnauthorizedQuizAction,
    InvalidQuizStructure,
)
from app.enums.roles import Roles


class QuizService:
    async def _check_user_permissions(
        self, uow: UnitOfWork, company_id: UUID, user_id: UUID
    ) -> None:
        company_items, _ = await uow.company.read(
            field="id", value=company_id, offset=0, limit=1
        )
        if not company_items:
            raise UnauthorizedQuizAction

        if company_items[0].owner_id == user_id:
            return

        memberships, _ = await uow.membership.read(
            field="user_id", value=user_id, offset=0, limit=100
        )

        allowed_roles = {Roles.ADMIN, Roles.OWNER}
        if any(
            m.company_id == company_id and m.role in allowed_roles and m.is_active
            for m in memberships
        ):
            return

        raise UnauthorizedQuizAction

    async def create_quiz(
        self,
        uow: UnitOfWork,
        data: QuizCreate,
        questions_data: QuestionsListCreate,
        current_user_id: UUID,
    ) -> QuizSchema:
        try:
            await self._check_user_permissions(uow, data.company_id, current_user_id)

            questions = questions_data.questions

            if len(questions) < 2:
                raise InvalidQuizStructure

            for question in questions:
                if not question.title:
                    raise InvalidQuizStructure
                options = question.answer_options
                if not (2 <= len(options) <= 4):
                    raise InvalidQuizStructure

                if not any(opt.is_correct for opt in options):
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

            quiz_with_questions, _ = await uow.quizzes.read(
                field="id",
                value=quiz.id,
                offset=0,
                limit=1,
                load_relationships=["questions", "company", "questions.answer_options"],
            )
            return QuizSchema.model_validate(quiz_with_questions[0])

        except (UnauthorizedQuizAction, InvalidQuizStructure):
            raise
        except Exception as e:
            logger.exception(f"Error while creating quiz: {e}")
            raise InternalErrorException

    async def read_quiz_by_id(
        self, uow: UnitOfWork, quiz_id: UUID, current_user_id: UUID
    ) -> QuizSchema | None:
        try:
            items, _ = await uow.quizzes.read(
                field="id",
                value=quiz_id,
                offset=0,
                limit=1,
                load_relationships=["questions", "company", "questions.answer_options"],
            )
            if not items:
                raise QuizNotFound

            quiz = items[0]

            memberships, _ = await uow.membership.read(
                field="user_id", value=current_user_id, offset=0, limit=100
            )

            active_memberships = [
                m
                for m in memberships
                if m.company_id == quiz.company.id and m.is_active
            ]
            if not active_memberships:
                raise UnauthorizedQuizAction

            return QuizSchema.model_validate(quiz)

        except (QuizNotFound, UnauthorizedQuizAction):
            raise
        except Exception as e:
            logger.exception(f"Error while reading quiz: {e}")
            raise InternalErrorException

    async def read_company_quizzes(
        self, uow: UnitOfWork, company_id: UUID, offset: int = 0, limit: int = 20
    ) -> QuizList:
        try:
            items, total = await uow.quizzes.read(
                field="company_id",
                value=company_id,
                offset=offset,
                limit=limit,
                load_relationships=["questions", "company", "questions.answer_options"],
            )

            quiz_schemas = [QuizSchema.model_validate(quiz) for quiz in items]
            return QuizList(quizzes=quiz_schemas, total=total)

        except Exception as e:
            logger.exception(f"Error while reading company quizzes: {e}")
            raise InternalErrorException

    async def update_quiz(
        self,
        uow: UnitOfWork,
        quiz_id: UUID,
        data: QuizUpdate,
        current_user_id: UUID,
    ) -> QuizSchema:
        try:
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
                            "id", option.id, **data.model_dump()
                        )
                    else:
                        await uow.answer_options.create(
                            question_id=new_question.id, **data.model_dump()
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

        except (QuizNotFound, UnauthorizedQuizAction):
            raise
        except Exception as e:
            logger.exception(f"Error while updating quiz: {e}")
            raise InternalErrorException

    async def delete_quiz(
        self, uow: UnitOfWork, quiz_id: UUID, current_user_id: UUID
    ) -> None:
        try:
            quiz = await self.read_quiz_by_id(uow, quiz_id, current_user_id)
            await self._check_user_permissions(uow, quiz.company_id, current_user_id)

            await uow.quizzes.delete_by("id", quiz_id)

        except (QuizNotFound, UnauthorizedQuizAction):
            raise
        except Exception as e:
            logger.exception(f"Error while deleting quiz: {e}")
            raise InternalErrorException
