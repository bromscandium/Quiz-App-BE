from uuid import UUID

from app.enums import Roles
from app.exceptions import (
    InvalidQuizAttempt,
    UnauthorizedQuizAttempt,
)
from app.schemas.quiz_attempt import (
    QuizAttemptCreate,
    QuizAttemptSchema,
    QuizAttemptsList,
)
from app.unit_of_work import UnitOfWork
from app.utils import LoggerUtil
from app.utils.redis import RedisUtil


class QuizAttemptService:
    def __init__(self):
        self.redis_util = RedisUtil()
        self.logger_util = LoggerUtil()

    async def _check_access(
        self,
        uow: UnitOfWork,
        current_user_id: UUID,
        company_id: UUID | None = None,
        quiz_attempt_id: UUID | None = None,
        require_admin_or_owner: bool = False,
    ) -> None:
        if quiz_attempt_id:
            quiz_attempt = await uow.quiz_attempts.read("id", quiz_attempt_id)
            if not quiz_attempt:
                self.logger_util.info("Unable to find quiz attempt")
                raise UnauthorizedQuizAttempt
            company_id = quiz_attempt.company_id
            if quiz_attempt.user_id == current_user_id:
                return

        memberships, _ = await uow.membership.read(
            field="user_id", value=current_user_id, offset=0, limit=100
        )

        for m in memberships:
            if not m.is_active:
                continue

            if company_id and m.company_id != company_id:
                continue

            if require_admin_or_owner and m.role not in {Roles.ADMIN, Roles.OWNER}:
                continue

            return

        self.logger_util.info("Cannot access quiz attempt")
        raise UnauthorizedQuizAttempt

    async def create_quiz_attempt(
        self, uow: UnitOfWork, data: QuizAttemptCreate, current_user_id: UUID
    ) -> QuizAttemptSchema:
        quizzes, _ = await uow.quizzes.read(
            field="id", value=data.quiz_id, offset=0, limit=1
        )

        if quizzes[0].company_id != data.company_id:
            self.logger_util.info("Cannot access quiz attempt")
            raise UnauthorizedQuizAttempt

        await self._check_access(uow, current_user_id, data.company_id)

        quizzes, _ = await uow.quizzes.read(
            field="id",
            value=data.quiz_id,
            offset=0,
            limit=1,
            load_relationships=["questions", "company", "questions.answer_options"],
        )
        if not quizzes:
            self.logger_util.info("Wrong quiz attempt")
            raise InvalidQuizAttempt

        if len(data.user_answers) != len(quizzes[0].questions):
            self.logger_util.info("Wrong length of quiz attempt")
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
                self.logger_util.info("Wrong answer option selection")
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

        await self.redis_util.save(
            obj=quiz_attempt, prefix="quiz_attempt", ttl_hours=48
        )

        return quiz_attempt

    async def read_quiz_attempt_by_id(
        self, uow: UnitOfWork, current_user_id: UUID, quiz_attempt_id: UUID
    ) -> QuizAttemptSchema | None:
        await self._check_access(
            uow=uow, current_user_id=current_user_id, quiz_attempt_id=quiz_attempt_id
        )

        cached = await self.redis_util.read(
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
            return None

        await self.redis_util.save(
            obj=quiz_attempts[0], prefix="quiz_attempt", ttl_hours=48
        )

        return QuizAttemptSchema.model_validate(quiz_attempts[0])

    async def read_users_quiz_attempts(
        self, uow: UnitOfWork, current_user_id: UUID, offset: int = 0, limit: int = 20
    ) -> QuizAttemptsList | None:
        cached_attempts = await self.redis_util.read_by_prefix(
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
            await self.redis_util.save(
                obj=quiz_attempts_schema, prefix="quiz_attempt", ttl_hours=48
            )

        return QuizAttemptsList(
            quiz_attempts=quiz_attempts_schemas + cached_attempts,
            total=total + len(cached_attempts),
        )

    async def read_company_quiz_attempts(
        self,
        uow: UnitOfWork,
        current_user_id: UUID,
        company_id: UUID,
        quiz_id: UUID | None,
        offset: int = 0,
        limit: int = 20,
    ) -> QuizAttemptsList | None:
        await self._check_access(
            current_user_id=current_user_id,
            uow=uow,
            company_id=company_id,
            require_admin_or_owner=True,
        )

        prefix = (
            "company_quiz_attempt_by_quiz"
            if quiz_id
            else "company_quiz_attempt_by_company"
        )

        cached_attempts = await self.redis_util.read_by_prefix(
            prefix=prefix, schema=QuizAttemptSchema
        )
        cached_ids = {cached_attempt.id for cached_attempt in cached_attempts}

        field, value = ("quiz_id", quiz_id) if quiz_id else ("company_id", company_id)

        quiz_attempts, total = await uow.quiz_attempts.read(
            field=field,
            value=value,
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
            schema = QuizAttemptSchema.model_validate(quiz_attempt)
            quiz_attempts_schemas.append(schema)
            await self.redis_util.save(obj=schema, prefix=prefix, ttl_hours=48)

        return QuizAttemptsList(
            quiz_attempts=quiz_attempts_schemas + cached_attempts,
            total=total + len(cached_attempts),
        )
