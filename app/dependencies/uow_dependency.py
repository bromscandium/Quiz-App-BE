from app.db.postgres import async_session
from app.unit_of_work.uow import UnitOfWork


async def get_uow():
    async with UnitOfWork(async_session) as uow:
        yield uow
