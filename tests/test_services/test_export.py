import json
import csv
import io
from uuid import uuid4

from app.exceptions import UnauthorizedCompanyOwner, QuizNotFound
from tests.factories.quiz_attempt import QuizAttemptCreateFactory
from tests.factories.user_answer import UserAnswerCreateFactory
from tests.conftest import redis_client
from tests.fixtures import *
from app.utils.redis import RedisClient


@pytest.mark.asyncio
async def test_export_json_by_quiz_success(
    uow, export_service, quiz_attempt_service, user_1, company_1, quiz_1, redis_client
):
    RedisClient.redis_client = redis_client

    user_answers = [
        UserAnswerCreateFactory.build(
            user_id=user_1.id,
            quiz_id=quiz_1.id,
            question_id=question.id,
            answer_option_id=question.answer_options[0].id,
            is_correct=True,
        )
        for question in quiz_1.questions
    ]

    attempt_data = QuizAttemptCreateFactory.build(
        quiz_id=quiz_1.id,
        company_id=company_1.id,
        user_id=user_1.id,
        user_answers=user_answers,
    )

    await quiz_attempt_service.create_quiz_attempt(uow, attempt_data, user_1.id)

    resp = await export_service.export_quiz_results(
        uow=uow,
        current_user_id=user_1.id,
        company_id=company_1.id,
        quiz_id=quiz_1.id,
        export_type="json",
    )

    assert resp.media_type == "application/json"
    assert "Content-Disposition" in resp.headers

    payload = json.loads(resp.body.decode())
    assert "quiz_attempts" in payload
    assert payload["total"] >= 1
    assert str(quiz_1.id) in {a["quiz_id"] for a in payload["quiz_attempts"]}


@pytest.mark.asyncio
async def test_export_csv_by_company_success(
    uow, export_service, quiz_attempt_service, user_1, company_1, quiz_1, redis_client
):
    RedisClient.redis_client = redis_client
    user_answers = [
        UserAnswerCreateFactory.build(
            user_id=user_1.id,
            quiz_id=quiz_1.id,
            question_id=question.id,
            answer_option_id=question.answer_options[0].id,
            is_correct=True,
        )
        for question in quiz_1.questions
    ]

    attempt_data = QuizAttemptCreateFactory.build(
        quiz_id=quiz_1.id,
        company_id=company_1.id,
        user_id=user_1.id,
        user_answers=user_answers,
    )

    await quiz_attempt_service.create_quiz_attempt(uow, attempt_data, user_1.id)

    resp = await export_service.export_quiz_results(
        uow=uow,
        current_user_id=user_1.id,
        company_id=company_1.id,
        quiz_id=None,
        export_type="csv",
    )

    assert resp.media_type == "text/csv"
    body = resp.body.decode()
    reader = csv.DictReader(io.StringIO(body))
    rows = list(reader)
    assert len(rows) >= 1
    assert set(reader.fieldnames) >= {
        "quiz_attempt_id",
        "user_id",
        "quiz_id",
        "correct_answers",
        "total_questions",
    }


@pytest.mark.asyncio
async def test_export_unauthorized_raises(uow, export_service, user_3, company_1):
    with pytest.raises(UnauthorizedCompanyOwner):
        await export_service.export_quiz_results(
            uow=uow,
            current_user_id=user_3.id,
            company_id=company_1.id,
            quiz_id=None,
            export_type="json",
        )


@pytest.mark.asyncio
async def test_export_quiz_not_found(uow, export_service, user_1, company_1):
    non_existent_quiz_id = uuid4()
    with pytest.raises(QuizNotFound):
        await export_service.export_quiz_results(
            uow=uow,
            current_user_id=user_1.id,
            company_id=company_1.id,
            quiz_id=non_existent_quiz_id,
            export_type="json",
        )
