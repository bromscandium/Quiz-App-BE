from app.models.request import Request
from app.repositories.base import BaseRepository


class RequestRepository(BaseRepository[Request]):
    def __init__(self, session):
        super().__init__(session, Request)
