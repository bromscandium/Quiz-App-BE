from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, DateTime, func


class IdMixin:
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, nullable=False
    )


class TimestampMixin:
    created_at: Mapped[DateTime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
