from datetime import datetime
from uuid import UUID

from app.schemas.base import Base
from app.schemas.user import UserSchema


class CompanySchema(Base):
    id: UUID
    owner: UserSchema | None = None
    name: str
    description: str | None = None
    visibility: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None


class CompanyCreate(Base):
    name: str
    description: str | None = None
    visibility: bool = True


class CompanyUpdate(Base):
    name: str | None = None
    description: str | None = None
    visibility: bool | None = None


class CompaniesList(Base):
    companies: list[CompanySchema] = []
    total: int = 0
