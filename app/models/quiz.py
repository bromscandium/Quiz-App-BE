import uuid

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import IdMixin, TimestampMixin


class Quiz(Base, IdMixin, TimestampMixin):
    __tablename__ = "quizzes"

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    frequency: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    company: Mapped["Company"] = relationship(back_populates="quizzes")

    questions: Mapped[list["Question"]] = relationship(
        back_populates="quiz", cascade="all, delete-orphan"
    )

    quiz_attempts: Mapped[list["QuizAttempt"]] = relationship(
        back_populates="quiz", cascade="all, delete-orphan"
    )
