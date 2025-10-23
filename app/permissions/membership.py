from fastapi import Depends
from uuid import UUID

from app.unit_of_work.uow import UnitOfWork
from app.exceptions.user import UnauthorizedUserActionException


async def check_owner_permission(
    current_user_id: UUID,
    uow: UnitOfWork = Depends(),
) -> bool:
    companies, _ = await uow.company.read(field="owner_id", value=current_user_id)

    if not companies:
        raise UnauthorizedUserActionException

    return True
