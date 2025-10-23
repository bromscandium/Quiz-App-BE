from sqlalchemy import DateTime, func, Boolean
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.types import Enum as SQLAEnum
from app.models import Base
from app.models.enums import Roles
from app.models.mixins import TimestampMixin, IdMixin, CompanyUserMixin


class Membership(Base, IdMixin, CompanyUserMixin, TimestampMixin):
    __tablename__ = "memberships"

    role: Mapped[Roles] = mapped_column(
        SQLAEnum(Roles, name="role"), default=Roles.MEMBER, nullable=False, index=True
    )
    joined_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=False
    )
    left_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, index=True
    )
