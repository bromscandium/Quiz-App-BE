from uuid import uuid4

from app.enums import Roles
from app.utils.redis import RedisClient
from app.exceptions import InvalidQuizAttempt, UnauthorizedQuizAttempt

from tests.factories.quiz_attempt import QuizAttemptCreateFactory
from tests.factories.user_answer import UserAnswerCreateFactory
from tests.factories.membership import MembershipCreateFactory
from tests.fixtures import *


@pytest.mark.asyncio
async def test_create_quiz_attempt_success(
    uow, quiz_attempt_service, user_1, company_1, quiz_1, redis_client
):
    RedisClient.redis_client = redis_client

    user_answers = [
        UserAnswerCreateFactory.build(
            question_id=question.id,
            answer_option_id=next(
                ao.id for ao in question.answer_options if ao.is_correct
            ),
        )
        for question in quiz_1.questions
    ]

    attempt_data = QuizAttemptCreateFactory.build(
        quiz_id=quiz_1.id, company_id=company_1.id, user_answers=user_answers
    )

    result = await quiz_attempt_service.create_quiz_attempt(
        uow, attempt_data, user_1.id
    )

    assert result.id is not None
    assert result.quiz_id == quiz_1.id
    assert result.user_id == user_1.id
    assert result.correct_answers == 2


@pytest.mark.asyncio
async def test_create_quiz_attempt_wrong_company(
    uow, quiz_attempt_service, user_1, company_2, quiz_1, redis_client
):
    RedisClient.redis_client = redis_client

    user_answers = [
        UserAnswerCreateFactory.build(
            question_id=q.id, answer_option_id=q.answer_options[0].id
        )
        for q in quiz_1.questions
    ]

    attempt_data = QuizAttemptCreateFactory.build(
        quiz_id=quiz_1.id, company_id=company_2.id, user_answers=user_answers
    )

    with pytest.raises(UnauthorizedQuizAttempt):
        await quiz_attempt_service.create_quiz_attempt(uow, attempt_data, user_1.id)


@pytest.mark.asyncio
async def test_create_quiz_attempt_wrong_answers_length(
    uow, quiz_attempt_service, user_1, company_1, quiz_1, redis_client
):
    from app.utils.redis import RedisClient

    RedisClient.redis_client = redis_client

    first_question = quiz_1.questions[0]

    user_answers = [
        UserAnswerCreateFactory.build(
            question_id=first_question.id,
            answer_option_id=first_question.answer_options[0].id,
        )
    ]

    attempt_data = QuizAttemptCreateFactory.build(
        quiz_id=quiz_1.id, company_id=company_1.id, user_answers=user_answers
    )

    with pytest.raises(InvalidQuizAttempt):
        await quiz_attempt_service.create_quiz_attempt(uow, attempt_data, user_1.id)


@pytest.mark.asyncio
async def test_create_quiz_attempt_invalid_answer_option(
    uow, quiz_attempt_service, user_1, company_1, quiz_1, redis_client
):
    RedisClient.redis_client = redis_client

    user_answers = [
        UserAnswerCreateFactory.build(question_id=q.id, answer_option_id=uuid4())
        for q in quiz_1.questions
    ]

    attempt_data = QuizAttemptCreateFactory.build(
        quiz_id=quiz_1.id, company_id=company_1.id, user_answers=user_answers
    )

    with pytest.raises(InvalidQuizAttempt):
        await quiz_attempt_service.create_quiz_attempt(uow, attempt_data, user_1.id)


@pytest.mark.asyncio
async def test_read_quiz_attempt_by_id_success(
    uow, quiz_attempt_service, user_1, company_1, quiz_1, redis_client
):
    RedisClient.redis_client = redis_client

    user_answers = [
        UserAnswerCreateFactory.build(
            question_id=q.id, answer_option_id=q.answer_options[0].id
        )
        for q in quiz_1.questions
    ]

    attempt_data = QuizAttemptCreateFactory.build(
        quiz_id=quiz_1.id, company_id=company_1.id, user_answers=user_answers
    )

    created = await quiz_attempt_service.create_quiz_attempt(
        uow, attempt_data, user_1.id
    )

    result = await quiz_attempt_service.read_quiz_attempt_by_id(
        uow, user_1.id, created.id
    )

    assert result.id == created.id
    assert result.user_id == user_1.id


@pytest.mark.asyncio
async def test_read_quiz_attempt_by_id_unauthorized(
    uow, quiz_attempt_service, user_1, user_2, company_1, quiz_1, redis_client
):
    RedisClient.redis_client = redis_client

    user_answers = [
        UserAnswerCreateFactory.build(
            question_id=q.id, answer_option_id=q.answer_options[0].id
        )
        for q in quiz_1.questions
    ]

    attempt_data = QuizAttemptCreateFactory.build(
        quiz_id=quiz_1.id, company_id=company_1.id, user_answers=user_answers
    )

    created = await quiz_attempt_service.create_quiz_attempt(
        uow, attempt_data, user_1.id
    )

    with pytest.raises(UnauthorizedQuizAttempt):
        await quiz_attempt_service.read_quiz_attempt_by_id(uow, user_2.id, created.id)


@pytest.mark.asyncio
async def test_read_users_quiz_attempts(
    uow, quiz_attempt_service, user_1, company_1, quiz_1, quiz_2, redis_client
):
    RedisClient.redis_client = redis_client

    for quiz in [quiz_1, quiz_2]:
        user_answers = [
            UserAnswerCreateFactory.build(
                question_id=q.id, answer_option_id=q.answer_options[0].id
            )
            for q in quiz.questions
        ]

        attempt_data = QuizAttemptCreateFactory.build(
            quiz_id=quiz.id, company_id=company_1.id, user_answers=user_answers
        )

        await quiz_attempt_service.create_quiz_attempt(uow, attempt_data, user_1.id)

    result = await quiz_attempt_service.read_users_quiz_attempts(
        uow, user_1.id, offset=0, limit=20
    )

    assert result.total >= 2
    assert len(result.quiz_attempts) >= 2


@pytest.mark.asyncio
async def test_read_company_quiz_attempts_by_company(
    uow,
    quiz_attempt_service,
    membership_service,
    user_1,
    user_2,
    company_1,
    quiz_1,
    redis_client,
):
    RedisClient.redis_client = redis_client

    membership_data = MembershipCreateFactory.build(
        user_id=user_2.id, company_id=company_1.id, role=Roles.ADMIN
    )
    await membership_service.create_membership(uow, membership_data)

    user_answers = [
        UserAnswerCreateFactory.build(
            question_id=q.id, answer_option_id=q.answer_options[0].id
        )
        for q in quiz_1.questions
    ]

    attempt_data = QuizAttemptCreateFactory.build(
        quiz_id=quiz_1.id, company_id=company_1.id, user_answers=user_answers
    )

    await quiz_attempt_service.create_quiz_attempt(uow, attempt_data, user_1.id)

    result = await quiz_attempt_service.read_company_quiz_attempts(
        uow, user_1.id, company_1.id, None, offset=0, limit=20
    )

    assert result.total >= 1


@pytest.mark.asyncio
async def test_read_company_quiz_attempts_by_quiz(
    uow, quiz_attempt_service, user_1, company_1, quiz_1, redis_client
):
    RedisClient.redis_client = redis_client

    user_answers = [
        UserAnswerCreateFactory.build(
            question_id=q.id, answer_option_id=q.answer_options[0].id
        )
        for q in quiz_1.questions
    ]

    attempt_data = QuizAttemptCreateFactory.build(
        quiz_id=quiz_1.id, company_id=company_1.id, user_answers=user_answers
    )

    await quiz_attempt_service.create_quiz_attempt(uow, attempt_data, user_1.id)

    result = await quiz_attempt_service.read_company_quiz_attempts(
        uow, user_1.id, company_1.id, quiz_1.id, offset=0, limit=20
    )

    assert result.total >= 1


@pytest.mark.asyncio
async def test_read_company_quiz_attempts_unauthorized(
    uow, quiz_attempt_service, user_2, company_1, redis_client
):
    RedisClient.redis_client = redis_client

    with pytest.raises(UnauthorizedQuizAttempt):
        await quiz_attempt_service.read_company_quiz_attempts(
            uow, user_2.id, company_1.id, None, offset=0, limit=20
        )
