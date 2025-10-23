from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base
from app.models.mixins import TimestampMixin, IdMixin, StatusMixin, CompanyUserMixin


class Invitation(Base, IdMixin, CompanyUserMixin, StatusMixin, TimestampMixin):
    __tablename__ = "invitations"

    invited_email: Mapped[str | None] = mapped_column(nullable=True, index=True)
