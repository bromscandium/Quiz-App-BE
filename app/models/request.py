from app.models import Base
from app.models.mixins import TimestampMixin, IdMixin, StatusMixin, CompanyUserMixin


class Request(Base, IdMixin, StatusMixin, CompanyUserMixin, TimestampMixin):
    __tablename__ = "requests"
