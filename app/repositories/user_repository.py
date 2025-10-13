from app.models.user_model import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session):
        super().__init__(session, User)
