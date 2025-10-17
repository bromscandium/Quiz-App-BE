from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

from app.models import Base
from app.models.mixins import TimestampMixin, IdMixin


class User(Base, IdMixin, TimestampMixin):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    surname: Mapped[str] = mapped_column(String(100), nullable=True)
    nickname: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(
        String(320), unique=True, nullable=False, index=True
    )
    hashed_password: Mapped[str] = mapped_column(String(1024), nullable=False)
