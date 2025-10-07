from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    func,
)
from sqlalchemy.orm import declared_attr


class IdMixin(object):
    @declared_attr
    def id(cls):
        return Column(Integer, primary_key=True, index=True, nullable=False)


class TimestampMixin(object):
    @declared_attr
    def created_at(cls):
        return Column(DateTime, default=func.now(), nullable=False)

    @declared_attr
    def updated_at(cls):
        return Column(DateTime, default=func.now(), nullable=False)
