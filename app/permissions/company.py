from fastapi import Depends
from uuid import UUID

from app.unit_of_work.uow import UnitOfWork


async def check_company_visibility(
    company_id: UUID,
    uow: UnitOfWork = Depends(),
) -> bool:
    company, _ = await uow.company.read(field="id", value=company_id, offset=0, limit=1)

    if company[0].visibility is False:
        return False

    return True
