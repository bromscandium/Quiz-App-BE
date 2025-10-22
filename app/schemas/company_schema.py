from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class CompanyBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")


class CompanySchema(CompanyBase):
    id: UUID
    owner_id: UUID
    name: str
    description: str | None = None
    visibility: bool | None = None


class CompanyCreate(CompanyBase):
    name: str
    description: str | None = None
    visibility: bool | None = None


class CompanyUpdateRequest(CompanyBase):
    name: str | None = None
    description: str | None = None
    visibility: bool | None = None


class CompaniesListResponse(CompanyBase):
    companies: list[CompanySchema] = []
    total: int = 0


class CompanyDetailResponse(CompanySchema):
    created_at: datetime | None = None
    updated_at: datetime | None = None
