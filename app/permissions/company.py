from uuid import UUID

from fastapi import Depends

from app.unit_of_work import UnitOfWork


async def check_company_visibility(
    company_id: UUID,
    uow: UnitOfWork = Depends(),
) -> bool:
    company, _ = await uow.company.read(field="id", value=company_id, offset=0, limit=1)

    return company[0].visibility
