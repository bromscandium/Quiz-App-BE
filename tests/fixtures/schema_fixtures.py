import pytest

from tests.factories.answer_option_factory import AnswerOptionCreateFactory
from tests.factories.question import QuestionsListCreateFactory, QuestionCreateFactory
from tests.factories.company import CompanyCreateFactory
from tests.factories.user import UserCreateFactory
from tests.factories.quiz import QuizCreateFactory
from tests.fixtures.service_fixtures import user_service, company_service, quiz_service


@pytest.fixture
def user_1_create():
    return UserCreateFactory.build(password="12345678")


@pytest.fixture
async def user_1(uow, user_service, user_1_create):
    return await user_service.create_user(uow, user_1_create)


@pytest.fixture
def user_2_create():
    return UserCreateFactory.build(password="12345678")


@pytest.fixture
async def user_2(uow, user_service, user_2_create):
    return await user_service.create_user(uow, user_2_create)


@pytest.fixture
def user_3_create():
    return UserCreateFactory.build(password="12345678")


@pytest.fixture
async def user_3(uow, user_service, user_3_create):
    return await user_service.create_user(uow, user_3_create)


@pytest.fixture
def company_1_create(user_1):
    return CompanyCreateFactory.build(owner_id=user_1.id, visibility=True)


@pytest.fixture
async def company_1(uow, company_service, user_1, company_1_create):
    return await company_service.create_company(uow, user_1.id, company_1_create)


@pytest.fixture
def company_2_create(user_2):
    return CompanyCreateFactory.build(owner_id=user_2.id, visibility=False)


@pytest.fixture
async def company_2(uow, company_service, user_2, company_2_create):
    return await company_service.create_company(uow, user_2.id, company_2_create)


@pytest.fixture
def questions_1_create():
    return QuestionsListCreateFactory.build(
        questions=[
            QuestionCreateFactory.build(
                title="What is the capital of France?",
                answer_options=[
                    AnswerOptionCreateFactory.build(text="Paris", is_correct=True),
                    AnswerOptionCreateFactory.build(text="London", is_correct=False),
                    AnswerOptionCreateFactory.build(text="Berlin", is_correct=False),
                ],
            ),
            QuestionCreateFactory.build(
                title="What is 2 + 2?",
                answer_options=[
                    AnswerOptionCreateFactory.build(text="3", is_correct=False),
                    AnswerOptionCreateFactory.build(text="4", is_correct=True),
                ],
            ),
        ]
    )


@pytest.fixture
def questions_1_one_question(questions_1_create):
    return QuestionsListCreateFactory.build(
        questions=[
            QuestionCreateFactory.build(
                title="What is the capital of France?",
                answer_options=[
                    AnswerOptionCreateFactory.build(text="Paris", is_correct=True),
                    AnswerOptionCreateFactory.build(text="London", is_correct=False),
                ],
            ),
        ]
    )


@pytest.fixture
def questions_1_two_questions_one_answer_each(questions_1_create):
    return QuestionsListCreateFactory.build(
        questions=[
            QuestionCreateFactory.build(
                title="What is the capital of France?",
                answer_options=[
                    AnswerOptionCreateFactory.build(text="Paris", is_correct=True),
                ],
            ),
            QuestionCreateFactory.build(
                title="What is 2 + 2?",
                answer_options=[
                    AnswerOptionCreateFactory.build(text="3", is_correct=False),
                ],
            ),
        ]
    )


@pytest.fixture
def quiz_1_create(company_1):
    return QuizCreateFactory.build(company_id=company_1.id)


@pytest.fixture
async def quiz_1(uow, quiz_service, quiz_1_create, questions_1_create, user_1):
    return await quiz_service.create_quiz(
        uow, quiz_1_create, questions_1_create, user_1.id
    )


@pytest.fixture
def quiz_2_create(company_1):
    return QuizCreateFactory.build(company_id=company_1.id)


@pytest.fixture
async def quiz_2(uow, quiz_service, quiz_2_create, questions_1_create, user_1):
    return await quiz_service.create_quiz(
        uow, quiz_2_create, questions_1_create, user_1.id
    )


@pytest.fixture
def quiz_3_create(company_1):
    return QuizCreateFactory.build(company_id=company_1.id)


@pytest.fixture
async def quiz_3(uow, quiz_service, quiz_3_create, questions_1_create, user_1):
    return await quiz_service.create_quiz(
        uow, quiz_3_create, questions_1_create, user_1.id
    )
