from typing import Generic, TypeVar, Optional, List, Type, Any, Dict
from sqlalchemy import select, update, delete
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

    async def read_by(self, field: str, value: Any) -> Optional[T]:
        field_attr = getattr(self.model, field)
        query = select(self.model).where(field_attr == value)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def read_all_by(
        self, field: str, value: Any, offset: int = 0, limit: int = 20
    ) -> List[T]:
        field_attr = getattr(self.model, field)
        query = (
            select(self.model).where(field_attr == value).offset(offset).limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def read_all(self, offset: int = 0, limit: int = 20) -> List[T]:
        query = select(self.model).offset(offset).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def update_by(self, field: str, value: Any, **update_data) -> Optional[T]:
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
