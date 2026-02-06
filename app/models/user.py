from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String

from app.models import Base


class User(Base):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    surname: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    nickname: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True, index=True
    )
    email: Mapped[str] = mapped_column(
        String(320), unique=True, nullable=False, index=True
    )
    hashed_password: Mapped[str] = mapped_column(String(1024), nullable=False)

    owned_companies: Mapped[list["Company"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )

    memberships: Mapped[list["Membership"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    company_actions: Mapped[list["CompanyActions"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    quiz_attempts: Mapped[list["QuizAttempt"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
