from tests.factories.quiz import QuizUpdateFactory
from tests.fixtures import *
from app.exceptions import InvalidQuizStructure, UnauthorizedQuizAction, QuizNotFound


@pytest.mark.asyncio
async def test_create_quiz_success(
    uow, quiz_service, questions_1_create, company_1, user_1
):
    quiz_data = QuizCreateFactory.build(company_id=company_1.id)
    quiz = await quiz_service.create_quiz(uow, quiz_data, questions_1_create, user_1.id)
    assert quiz.id is not None
    assert quiz.title == quiz_data.title
    assert len(quiz.questions) == 2


@pytest.mark.asyncio
async def test_create_quiz_invalid_structure_less_questions(
    uow, quiz_service, questions_1_one_question, company_1, user_1
):
    quiz_data = QuizCreateFactory.build(company_id=company_1.id)
    with pytest.raises(InvalidQuizStructure):
        await quiz_service.create_quiz(
            uow, quiz_data, questions_1_one_question, user_1.id
        )


@pytest.mark.asyncio
async def test_create_quiz_invalid_structure_no_correct_option(
    uow, quiz_service, questions_1_two_questions_one_answer_each, company_1, user_1
):
    quiz_data = QuizCreateFactory.build(company_id=company_1.id)
    with pytest.raises(InvalidQuizStructure):
        await quiz_service.create_quiz(
            uow, quiz_data, questions_1_two_questions_one_answer_each, user_1.id
        )


@pytest.mark.asyncio
async def test_create_quiz_unauthorized_user(
    uow, quiz_service, questions_1_create, company_1, user_2
):
    quiz_data = QuizCreateFactory.build(company_id=company_1.id)
    with pytest.raises(UnauthorizedQuizAction):
        await quiz_service.create_quiz(uow, quiz_data, questions_1_create, user_2.id)


@pytest.mark.asyncio
async def test_read_quiz_by_id_success(
    uow, quiz_service, questions_1_create, company_1, user_1
):
    quiz_data = QuizCreateFactory.build(company_id=company_1.id)
    quiz = await quiz_service.create_quiz(uow, quiz_data, questions_1_create, user_1.id)
    read_quiz = await quiz_service.read_quiz_by_id(uow, quiz.id, user_1.id)
    assert read_quiz.id == quiz.id


@pytest.mark.asyncio
async def test_read_quiz_by_id_unauthorized(
    uow, quiz_service, questions_1_create, company_1, user_2
):
    quiz_data = QuizCreateFactory.build(company_id=company_1.id)
    quiz = await quiz_service.create_quiz(
        uow, quiz_data, questions_1_create, company_1.owner.id
    )
    with pytest.raises(UnauthorizedQuizAction):
        await quiz_service.read_quiz_by_id(uow, quiz.id, user_2.id)


@pytest.mark.asyncio
async def test_read_company_quizzes_success(
    uow, quiz_service, questions_1_create, company_1, user_1
):
    quiz_data = QuizCreateFactory.build(company_id=company_1.id)
    await quiz_service.create_quiz(uow, quiz_data, questions_1_create, user_1.id)
    result = await quiz_service.read_company_quizzes(uow, company_1.id)
    assert result.total >= 1


@pytest.mark.asyncio
async def test_update_quiz_success(
    uow, quiz_service, questions_1_create, company_1, user_1
):
    quiz_data = QuizCreateFactory.build(company_id=company_1.id)
    quiz = await quiz_service.create_quiz(uow, quiz_data, questions_1_create, user_1.id)

    quiz_update = QuizUpdateFactory.build(title="Updated title")
    updated = await quiz_service.update_quiz(uow, quiz.id, quiz_update, user_1.id)

    assert updated.title == "Updated title"


@pytest.mark.asyncio
async def test_update_quiz_unauthorized(
    uow, quiz_service, questions_1_create, company_1, user_2
):
    quiz_data = QuizCreateFactory.build(company_id=company_1.id)
    quiz = await quiz_service.create_quiz(
        uow, quiz_data, questions_1_create, company_1.owner.id
    )

    quiz_update = QuizUpdateFactory.build(title="Updated title")
    with pytest.raises(UnauthorizedQuizAction):
        await quiz_service.update_quiz(uow, quiz.id, quiz_update, user_2.id)


@pytest.mark.asyncio
async def test_delete_quiz_success(
    uow, quiz_service, questions_1_create, company_1, user_1
):
    quiz_data = QuizCreateFactory.build(company_id=company_1.id)
    quiz = await quiz_service.create_quiz(uow, quiz_data, questions_1_create, user_1.id)
    deleted = await quiz_service.delete_quiz(uow, quiz.id, user_1.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_delete_quiz_unauthorized(
    uow, quiz_service, questions_1_create, company_1, user_2
):
    quiz_data = QuizCreateFactory.build(company_id=company_1.id)
    quiz = await quiz_service.create_quiz(
        uow, quiz_data, questions_1_create, company_1.owner.id
    )
    with pytest.raises(UnauthorizedQuizAction):
        await quiz_service.delete_quiz(uow, quiz.id, user_2.id)
