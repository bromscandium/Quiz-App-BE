from app.models.user_answer import UserAnswer
from app.repositories.base import BaseRepository


class UserAnswerRepository(BaseRepository[UserAnswer]):
    def __init__(self, session):
        super().__init__(session, UserAnswer)
