from app.models.refresh_token_model import RefreshToken
from app.repositories.base_repository import BaseRepository


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    def __init__(self, session):
        super().__init__(session, RefreshToken)
