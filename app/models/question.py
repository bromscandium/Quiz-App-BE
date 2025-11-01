import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import IdMixin, TimestampMixin


class Question(Base, IdMixin, TimestampMixin):
    __tablename__ = "questions"

    quiz_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("quizzes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)

    quiz: Mapped["Quiz"] = relationship(back_populates="questions")

    answer_options: Mapped[list["AnswerOption"]] = relationship(
        back_populates="question", cascade="all, delete-orphan"
    )

    user_answers: Mapped[list["UserAnswer"]] = relationship(
        back_populates="question", cascade="all, delete-orphan"
    )
