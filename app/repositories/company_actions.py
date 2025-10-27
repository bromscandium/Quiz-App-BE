from app.models import CompanyActions
from app.repositories.base import BaseRepository


class CompanyActionsRepository(BaseRepository[CompanyActions]):
    def __init__(self, session):
        super().__init__(session, CompanyActions)
