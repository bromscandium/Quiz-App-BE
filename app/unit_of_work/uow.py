from __future__ import annotations
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.repositories.answer_option import AnswerOptionRepository
from app.repositories.question import QuestionRepository
from app.repositories.quiz import QuizRepository
from app.repositories.quiz_attempt import QuizAttemptRepository
from app.repositories.user import UserRepository
from app.repositories.company import CompanyRepository
from app.repositories.membership import MembershipRepository
from app.repositories.company_actions import CompanyActionsRepository
from app.repositories.user_answer import UserAnswerRepository


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
