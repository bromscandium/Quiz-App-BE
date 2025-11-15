from datetime import datetime, timedelta

from app.utils.redis import RedisClient
from app.enums import Roles
from app.exceptions import UnauthorizedQuizAction

from tests.factories.quiz_attempt import QuizAttemptCreateFactory
from tests.factories.user_answer import UserAnswerCreateFactory
from tests.factories.membership import MembershipCreateFactory
from tests.fixtures import *


@pytest.mark.asyncio
async def test_read_user_stats(
    uow, stats_service, quiz_attempt_service, user_1, company_1, quiz_1, redis_client
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

    await quiz_attempt_service.create_quiz_attempt(uow, attempt_data, user_1.id)

    result = await stats_service.read_user_stats(
        uow, user_1.id, company_id=company_1.id
    )

    assert result.user_id == user_1.id
    assert result.total_correct_answers == len(quiz_1.questions)
    assert result.total_answered_questions == len(quiz_1.questions)
    assert result.average_score == 100.0


@pytest.mark.asyncio
async def test_read_user_stats_with_quiz_filter(
    uow, stats_service, quiz_attempt_service, user_1, company_1, quiz_1, redis_client
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

    result = await stats_service.read_user_stats(
        uow, user_1.id, quiz_id=quiz_1.id, company_id=company_1.id
    )

    assert result.user_id == user_1.id
    assert result.total_answered_questions > 0


@pytest.mark.asyncio
async def test_read_user_stats_with_date_range(
    uow, stats_service, quiz_attempt_service, user_1, company_1, quiz_1, redis_client
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

    start_date = datetime.now() - timedelta(days=1)
    end_date = datetime.now() + timedelta(days=1)

    result = await stats_service.read_user_stats(
        uow,
        user_1.id,
        company_id=company_1.id,
        start_date=start_date,
        end_date=end_date,
    )

    assert result.user_id == user_1.id
    assert result.start_date == start_date
    assert result.end_date == end_date


@pytest.mark.asyncio
async def test_read_user_stats_no_attempts(uow, stats_service, user_1, company_1):
    result = await stats_service.read_user_stats(
        uow, user_1.id, company_id=company_1.id
    )

    assert result.user_id == user_1.id
    assert result.total_correct_answers == 0
    assert result.total_answered_questions == 0
    assert result.average_score == 0.0


@pytest.mark.asyncio
async def test_read_user_stats_quizzes(
    uow,
    stats_service,
    quiz_attempt_service,
    user_1,
    company_1,
    quiz_1,
    quiz_2,
    redis_client,
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

    result = await stats_service.read_user_stats_quizzes(
        uow, user_1.id, company_id=company_1.id
    )

    assert len(result.user_attempts) >= 2
    for attempt in result.user_attempts:
        assert attempt.quiz_id in [quiz_1.id, quiz_2.id]
        assert attempt.attempts_count > 0


@pytest.mark.asyncio
async def test_read_user_stats_last_attempts(
    uow, stats_service, quiz_attempt_service, user_1, company_1, quiz_1, redis_client
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

    result = await stats_service.read_user_stats_last_attempts(
        uow, user_1.id, company_id=company_1.id
    )

    assert len(result.user_attempts) >= 1
    assert result.user_attempts[0].quiz_id == quiz_1.id
    assert result.user_attempts[0].last_attempt_at is not None


@pytest.mark.asyncio
async def test_read_company_users_stats(
    uow,
    stats_service,
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

    result = await stats_service.read_company_users_stats(uow, user_1.id, company_1.id)

    assert result is not None
    assert len(result.user_stats) >= 1


@pytest.mark.asyncio
async def test_read_company_users_stats_unauthorized(
    uow, stats_service, user_2, company_1
):
    with pytest.raises(UnauthorizedQuizAction):
        await stats_service.read_company_users_stats(uow, user_2.id, company_1.id)


@pytest.mark.asyncio
async def test_read_company_users_stats_with_dates(
    uow, stats_service, quiz_attempt_service, user_1, company_1, quiz_1, redis_client
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

    start_date = datetime.now() - timedelta(days=1)
    end_date = datetime.now() + timedelta(days=1)

    result = await stats_service.read_company_users_stats(
        uow, user_1.id, company_1.id, start_date=start_date, end_date=end_date
    )

    assert result is not None


@pytest.mark.asyncio
async def test_read_company_user_quizzes_stats(
    uow, stats_service, quiz_attempt_service, user_1, company_1, quiz_1, redis_client
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

    result = await stats_service.read_company_user_quizzes_stats(
        uow, user_1.id, company_1.id, user_1.id
    )

    assert result is not None
    assert len(result.quiz_stats) >= 1


@pytest.mark.asyncio
async def test_read_company_user_quizzes_stats_unauthorized(
    uow, stats_service, user_1, user_2, company_1
):
    with pytest.raises(UnauthorizedQuizAction):
        await stats_service.read_company_user_quizzes_stats(
            uow, user_2.id, company_1.id, user_1.id
        )


@pytest.mark.asyncio
async def test_read_company_users_last_attempts(
    uow, stats_service, quiz_attempt_service, user_1, company_1, quiz_1, redis_client
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

    result = await stats_service.read_company_users_last_attempts(
        uow, user_1.id, company_1.id
    )

    assert result is not None
    assert len(result.user_attempts) >= 1


@pytest.mark.asyncio
async def test_read_company_users_last_attempts_unauthorized(
    uow, stats_service, user_2, company_1
):
    with pytest.raises(UnauthorizedQuizAction):
        await stats_service.read_company_users_last_attempts(
            uow, user_2.id, company_1.id
        )
