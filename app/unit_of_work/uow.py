from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.repositories import (
    AnswerOptionRepository,
    CompanyRepository,
    CompanyActionsRepository,
    MembershipRepository,
    QuestionRepository,
    QuizRepository,
    QuizAttemptRepository,
    StatsRepository,
    UserRepository,
    UserAnswerRepository,
    NotificationRepository,
    UserNotificationRepository,
)


class UnitOfWork:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

    async def __aenter__(self) -> "UnitOfWork":
        self.session = self._session_factory()
        self.users = UserRepository(self.session)
        self.company = CompanyRepository(self.session)
        self.membership = MembershipRepository(self.session)
        self.company_actions = CompanyActionsRepository(self.session)
        self.quizzes = QuizRepository(self.session)
        self.questions = QuestionRepository(self.session)
        self.answer_options = AnswerOptionRepository(self.session)
        self.quiz_attempts = QuizAttemptRepository(self.session)
        self.user_answers = UserAnswerRepository(self.session)
        self.stats = StatsRepository(self.session)
        self.notifications = NotificationRepository(self.session)
        self.user_notifications = UserNotificationRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        try:
            if exc_type:
                await self.session.rollback()
            else:
                await self.session.commit()
        finally:
            await self.session.close()
            self.session = None

    async def commit(self) -> None:
        if self.session:
            await self.session.commit()

    async def rollback(self) -> None:
        if self.session:
            await self.session.rollback()
