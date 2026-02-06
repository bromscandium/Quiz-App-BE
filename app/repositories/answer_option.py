from app.models.answer_option import AnswerOption
from app.repositories.base import BaseRepository


class AnswerOptionRepository(BaseRepository[AnswerOption]):
    def __init__(self, session):
        super().__init__(session, AnswerOption)
