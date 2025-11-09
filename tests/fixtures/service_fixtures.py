import pytest
from app.services import (
    AuthService,
    UserService,
    CompanyService,
    CompanyActionsService,
    MembershipService,
    QuizService,
    QuizAttemptService,
    StatsService,
    ExportService,
)
from app.services.notification import NotificationService


@pytest.fixture
def auth_service():
    return AuthService()


@pytest.fixture
def user_service():
    return UserService()


@pytest.fixture
def company_service():
    return CompanyService()


@pytest.fixture
def company_actions_service():
    return CompanyActionsService()


@pytest.fixture
def membership_service():
    return MembershipService()


@pytest.fixture
def notification_service():
    return NotificationService()


@pytest.fixture
def quiz_service():
    return QuizService()


@pytest.fixture
def quiz_attempt_service():
    return QuizAttemptService()


@pytest.fixture
def stats_service():
    return StatsService()


@pytest.fixture
def export_service():
    return ExportService()
