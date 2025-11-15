from uuid import UUID

from app.unit_of_work import UnitOfWork


async def check_owner_permission(
    current_user_id: UUID,
    uow: UnitOfWork,
    company_id: UUID,
) -> bool:
    company, _ = await uow.company.read(field="id", value=company_id, offset=0, limit=1)

    return bool(company and company[0].owner_id == current_user_id)
