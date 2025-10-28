from app.models.quiz_attempt import QuizAttempt
from app.repositories.base import BaseRepository


class QuizAttemptRepository(BaseRepository[QuizAttempt]):
    def __init__(self, session):
        super().__init__(session, QuizAttempt)
