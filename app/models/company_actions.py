import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Enum as SQLAEnum

from app.enums.action_types import ActionTypes
from app.enums.action_statuses import ActionStatuses
from app.models.base import Base


class CompanyActions(Base):
    __tablename__ = "company_actions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
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
    action_type: Mapped[ActionTypes] = mapped_column(
        SQLAEnum(ActionTypes, name="action_type"), index=True, nullable=False
    )
    invited_email: Mapped[str] = mapped_column(
        String(320), unique=True, nullable=True, index=True
    )
    status: Mapped[ActionStatuses] = mapped_column(
        SQLAEnum(ActionStatuses, name="status"), index=True, nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="company_actions")

    company: Mapped["Company"] = relationship(back_populates="company_actions")
