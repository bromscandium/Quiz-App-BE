from app.models.invitation import Invitation
from app.repositories.base import BaseRepository


class InvitationRepository(BaseRepository[Invitation]):
    def __init__(self, session):
        super().__init__(session, Invitation)
