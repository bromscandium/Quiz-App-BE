import uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID

from app.models import Base
from app.models.mixins import TimestampMixin, IdMixin


class Company(Base, IdMixin, TimestampMixin):
    __tablename__ = "companies"

    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    visibility: Mapped[bool] = mapped_column(Boolean, nullable=False, index=True)
