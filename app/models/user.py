from sqlalchemy import (
    Column,
    String,
)
from sqlalchemy.orm import declarative_base

from app.models.mixins import TimestampMixin, IdMixin

Base = declarative_base()


class User(Base, IdMixin, TimestampMixin):
    __tablename__ = "users"

    name = Column(String(length=100))
    surname = Column(String(length=100))
    nickname = Column(String(length=100), nullable=False, unique=True)
    email = Column(String(length=320), unique=True, nullable=False, index=True)
    hashed_password = Column(String(length=1024), nullable=False)

    # DONT FORGET TO ERASE, it shows text format of user's data, dev purposes
    def __repr__(self):
        return f"<User {self.id}, {self.name}, {self.surname}, {self.nickname}, {self.email}, {self.hashed_password},{self.created_at}, {self.updated_at}>"
