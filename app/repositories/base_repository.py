from typing import Generic, TypeVar, Type, Any
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class BaseRepository(Generic[T]):
    def __init__(self, session: AsyncSession, model: Type[T]):
        self.session = session
        self.model = model

    async def create(self, **kwargs) -> T:
        obj = self.model(**kwargs)
        self.session.add(obj)
        return obj

    async def read(
        self,
        field: str | None = None,
        value: Any | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[T], int]:
        query = select(self.model)
        count_query = select(func.count()).select_from(self.model)

        if field and value is not None:
            field_attr = getattr(self.model, field)
            query = query.where(field_attr == value)
            count_query = count_query.where(field_attr == value)

        query = query.offset(offset).limit(limit)

        result = await self.session.execute(query)
        count_result = await self.session.execute(count_query)
        items: list[T] = result.scalars().all()
        total_count: int = count_result.scalar_one()

        return items, total_count

    async def update_by(self, field: str, value: Any, **update_data) -> T | None:
        field_attr = getattr(self.model, field)
        query = (
            update(self.model)
            .where(field_attr == value)
            .values(**update_data)
            .returning(self.model)
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def delete_by(self, field: str, value: Any) -> None:
        field_attr = getattr(self.model, field)
        query = delete(self.model).where(field_attr == value)
        await self.session.execute(query)
