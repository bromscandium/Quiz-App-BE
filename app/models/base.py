from sqlalchemy.orm import DeclarativeBase

from app.models.mixins import IdMixin, TimestampMixin


class Base(DeclarativeBase, IdMixin, TimestampMixin):
    pass
