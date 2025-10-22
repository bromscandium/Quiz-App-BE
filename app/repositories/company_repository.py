from app.models.company_model import Company
from app.repositories.base_repository import BaseRepository


class CompanyRepository(BaseRepository[Company]):
    def __init__(self, session):
        super().__init__(session, Company)
