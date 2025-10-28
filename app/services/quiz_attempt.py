from uuid import UUID

from app.exceptions.base import InternalErrorException
from app.unit_of_work.uow import UnitOfWork
from app.schemas.quiz_attempt import (
    QuizAttemptSchema,
    QuizAttemptCreate,
    UserStats,
    QuizAttemptsList,
)

from app.utils.logger import logger
from app.exceptions.quiz_attempt import (
    QuizAttemptNotFound,
    InvalidQuizAttempt,
    QuizNotAccessible,
    UnauthorizedQuizAttempt,
)
from app.utils.redis import RedisUtil


class QuizAttemptService:
    def __init__(self):
        self.redis = RedisUtil()

    async def _check_quiz_access(
        self, uow: UnitOfWork, quiz_id: UUID, company_id: UUID
    ) -> None:
        quizzes, _ = await uow.quizzes.read(
            field="id", value=quiz_id, offset=0, limit=1
        )

        if quizzes[0].company_id != company_id:
            raise QuizNotAccessible

    async def _check_user_membership(
        self, uow: UnitOfWork, user_id: UUID, company_id: UUID
    ) -> None:
        memberships, _ = await uow.membership.read(
            field="user_id", value=user_id, offset=0, limit=100
        )

        for m in memberships:
            if m.company_id == company_id and m.is_active:
                return

        raise QuizNotAccessible

    async def create_quiz_attempt(
        self, uow: UnitOfWork, data: QuizAttemptCreate, current_user_id: UUID
    ) -> QuizAttemptSchema:
        try:
            await self._check_quiz_access(uow, data.quiz_id, data.company_id)
            await self._check_user_membership(uow, current_user_id, data.company_id)

            quizzes, _ = await uow.quizzes.read(
                field="id",
                value=data.quiz_id,
                offset=0,
                limit=1,
                load_relationships=["questions", "company", "questions.answer_options"],
            )
            if not quizzes:
                raise InvalidQuizAttempt

            if len(data.user_answers) != len(quizzes[0].questions):
                raise InvalidQuizAttempt

            correct_answers = 0

            quiz_attempt = await uow.quiz_attempts.create(
                user_id=current_user_id,
                quiz_id=data.quiz_id,
                company_id=data.company_id,
                correct_answers=0,
                total_questions=len(quizzes[0].questions),
            )
            await uow.session.flush()

            for user_answer in data.user_answers:
                answer_option_items, _ = await uow.answer_options.read(
                    field="id", value=user_answer.answer_option_id, offset=0, limit=1
                )
                if not answer_option_items:
                    raise InvalidQuizAttempt

                answer_option = answer_option_items[0]
                is_correct = answer_option.is_correct

                if is_correct:
                    correct_answers += 1

                await uow.user_answers.create(
                    quiz_attempt_id=quiz_attempt.id,
                    question_id=user_answer.question_id,
                    answer_option_id=user_answer.answer_option_id,
                    is_correct=is_correct,
                )

            quiz_attempt.correct_answers = correct_answers
            await uow.session.flush()

            await uow.session.refresh(quiz_attempt, attribute_names=["user_answers"])

            quiz_attempts, _ = await uow.quiz_attempts.read(
                field="id",
                value=quiz_attempt.id,
                offset=0,
                limit=1,
                load_relationships=[
                    "user_answers",
                    "user",
                    "company",
                    "company.owner",
                    "quiz",
                    "quiz.questions",
                    "quiz.questions.answer_options",
                ],
            )

            quizzes[0].frequency += 1
            await uow.session.flush()

            quiz_attempt = QuizAttemptSchema.model_validate(quiz_attempts[0])

            await self.redis.save(obj=quiz_attempt, prefix="quiz_attempt", ttl_hours=48)

            return quiz_attempt

        except (InvalidQuizAttempt, QuizNotAccessible):
            raise
        except Exception as e:
            logger.exception(f"Error while submitting quiz attempt: {e}")
            raise InternalErrorException

    async def read_quiz_attempt_by_id(
        self, uow: UnitOfWork, quiz_attempt_id: UUID
    ) -> QuizAttemptSchema | None:
        try:
            cached = await self.redis.read(
                quiz_attempt_id, QuizAttemptSchema, "quiz_attempt"
            )
            if cached:
                return cached

            quiz_attempts, _ = await uow.quiz_attempts.read(
                field="id",
                value=quiz_attempt_id,
                offset=0,
                limit=1,
                load_relationships=[
                    "user_answers",
                    "user",
                    "company",
                    "company.owner",
                    "quiz",
                    "quiz.questions",
                    "quiz.questions.answer_options",
                ],
            )
            if not quiz_attempts:
                raise None

            await self.redis.save(
                obj=quiz_attempts[0], prefix="quiz_attempt", ttl_hours=48
            )

            return QuizAttemptSchema.model_validate(quiz_attempts[0])

        except Exception as e:
            logger.exception(f"Error while getting quiz attempt: {e}")
            raise InternalErrorException

    async def read_users_quiz_attempts(
        self, uow: UnitOfWork, current_user_id: UUID, offset: int = 0, limit: int = 20
    ) -> QuizAttemptsList | None:
        try:
            cached_attempts = await self.redis.read_by_prefix(
                prefix="quiz_attempt", schema=QuizAttemptSchema
            )
            cached_ids = {cached_attempt.id for cached_attempt in cached_attempts}

            quiz_attempts, total = await uow.quiz_attempts.read(
                field="user_id",
                value=current_user_id,
                offset=offset,
                exclude_ids=cached_ids,
                limit=limit,
                load_relationships=[
                    "user_answers",
                    "user",
                    "company",
                    "company.owner",
                    "quiz",
                    "quiz.questions",
                    "quiz.questions.answer_options",
                ],
            )

            quiz_attempts_schemas = []

            for quiz_attempt in quiz_attempts:
                quiz_attempts_schema = QuizAttemptSchema.model_validate(quiz_attempt)
                quiz_attempts_schemas.append(quiz_attempts_schema)
                await self.redis.save(
                    obj=quiz_attempts_schema, prefix="quiz_attempt", ttl_hours=48
                )

            return QuizAttemptsList(
                quiz_attempts=quiz_attempts_schemas + cached_attempts,
                total=total + len(cached_attempts),
            )

        except Exception as e:
            logger.exception(f"Error while reading user quiz attempts: {e}")
            raise InternalErrorException

    async def read_user_stats(
        self,
        uow: UnitOfWork,
        user_id: UUID,
        quiz_id: UUID | None = None,
        company_id: UUID | None = None,
    ) -> UserStats:
        try:
            result = await uow.stats.calculate_stats(
                user_id=user_id, quiz_id=quiz_id, company_id=company_id
            )

            average_score = (
                round(
                    (result.total_correct or 0) / (result.total_questions or 1) * 100, 2
                )
                if result
                else 0.0
            )

            return UserStats(
                user_id=user_id,
                company_id=company_id,
                total_correct_answers=(result.total_correct or 0) if result else 0,
                total_answered_questions=(result.total_questions or 0) if result else 0,
                average_score=(average_score or 0) if result else 0,
                last_attempt_at=result.last_attempt if result else None,
            )

        except Exception as e:
            logger.exception(f"Error while getting user stats: {e}")
            raise InternalErrorException

    async def delete_user_attempt(
        self, uow: UnitOfWork, quiz_attempt_id: UUID, current_user_id: UUID
    ) -> None:
        try:
            quiz_attempts, _ = await uow.quiz_attempts.read(
                field="id",
                value=quiz_attempt_id,
                offset=0,
                limit=1,
            )

            if not quiz_attempts:
                raise QuizAttemptNotFound

            if quiz_attempts[0].user_id != current_user_id:
                raise UnauthorizedQuizAttempt

            await uow.quiz_attempts.delete_by("id", quiz_attempt_id)
            await uow.session.flush()
        except QuizAttemptNotFound:
            raise
        except Exception as e:
            logger.exception(f"Error while deleting quiz_attempt: {e}")
            raise InternalErrorException
