import uuid

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Company(Base):
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

    owner: Mapped["User"] = relationship(back_populates="owned_companies")

    memberships: Mapped[list["Membership"]] = relationship(
        back_populates="company", cascade="all, delete-orphan"
    )

    company_actions: Mapped[list["CompanyActions"]] = relationship(
        back_populates="company", cascade="all, delete-orphan"
    )

    quizzes: Mapped[list["Quiz"]] = relationship(
        back_populates="company", cascade="all, delete-orphan"
    )

    quiz_attempts: Mapped[list["QuizAttempt"]] = relationship(
        back_populates="company", cascade="all, delete-orphan"
    )

    notifications: Mapped[list["Notification"]] = relationship(
        back_populates="company", cascade="all, delete-orphan"
    )
