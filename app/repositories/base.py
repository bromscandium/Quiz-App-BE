from typing import Generic, TypeVar, Type, Any
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import selectinload, joinedload
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
        load_relationships: list[str] | None = None,
        use_joined_load=True,
    ) -> tuple[list[T], int]:
        query = select(self.model)
        count_query = select(func.count()).select_from(self.model)

        if field and value is not None:
            field_attr = getattr(self.model, field)
            query = query.where(field_attr == value)
            count_query = count_query.where(field_attr == value)

        if load_relationships:
            loader = joinedload if use_joined_load else selectinload
            for relationship in load_relationships:
                if "." in relationship:
                    parts = relationship.split(".")
                    current_loader = loader(getattr(self.model, parts[0]))

                    related_attr = getattr(self.model, parts[0])
                    if hasattr(related_attr.property, "mapper"):
                        related_model = related_attr.property.mapper.class_

                        for part in parts[1:]:
                            current_loader = current_loader.selectinload(
                                getattr(related_model, part)
                            )
                            next_attr = getattr(related_model, part)
                            if hasattr(next_attr.property, "mapper"):
                                related_model = next_attr.property.mapper.class_

                    query = query.options(current_loader)
                else:
                    query = query.options(loader(getattr(self.model, relationship)))

        query = query.offset(offset).limit(limit)

        result = await self.session.execute(query)
        count_result = await self.session.execute(count_query)

        items: list[T] = result.unique().scalars().all()
        total_count: int = count_result.scalar_one()

        return items, total_count

    async def update_by(self, field: str, value: Any, **update_data) -> T | None:
        field_attr = getattr(self.model, field)
        await self.session.execute(
            update(self.model).where(field_attr == value).values(**update_data)
        )
        await self.session.commit()

        stmt = select(self.model).where(field_attr == value).options(selectinload("*"))
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def delete_by(self, field: str, value: Any) -> None:
        field_attr = getattr(self.model, field)
        query = delete(self.model).where(field_attr == value)
        await self.session.execute(query)
