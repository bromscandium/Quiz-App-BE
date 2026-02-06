from sqlalchemy.orm import DeclarativeBase

from app.models.mixins import TimestampMixin, IdMixin


class Base(DeclarativeBase, IdMixin, TimestampMixin):
    pass
