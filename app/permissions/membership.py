from uuid import UUID
from app.unit_of_work.uow import UnitOfWork
from app.exceptions.company import NotOwnerOfCompany


async def check_owner_permission(
    current_user_id: UUID,
    uow: UnitOfWork,
    company_id: UUID,
) -> bool:
    company, _ = await uow.company.read(field="id", value=company_id, offset=0, limit=1)

    is_owner = bool(company and company[0].owner_id == current_user_id)

    if not is_owner:
        raise NotOwnerOfCompany

    return is_owner
