from uuid import UUID

from app.schemas.base import Base
from app.schemas.mixins import TimeStamp


class CompanySchema(Base):
    id: UUID
    owner_id: UUID
    name: str
    description: str | None = None
    visibility: bool | None = None


class CompanyCreateRequest(Base):
    name: str
    description: str | None = None
    visibility: bool | None = None


class CompanyUpdateRequest(Base):
    name: str | None = None
    description: str | None = None
    visibility: bool | None = None


class CompaniesListResponse(Base):
    companies: list[CompanySchema] = []
    total: int = 0


class CompanyDetailResponse(CompanySchema, TimeStamp):
    pass
