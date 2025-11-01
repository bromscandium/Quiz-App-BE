import uuid

from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Enum as SQLAEnum

from app.enums.roles import Roles
from app.models.base import Base


class Membership(Base):
    __tablename__ = "memberships"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    role: Mapped[Roles] = mapped_column(
        SQLAEnum(Roles, name="role"), default=Roles.MEMBER, nullable=False, index=True
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, index=True
    )

    user: Mapped["User"] = relationship(back_populates="memberships")

    company: Mapped["Company"] = relationship(back_populates="memberships")
