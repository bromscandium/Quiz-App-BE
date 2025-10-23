import enum


class Roles(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"  # for future 10th task, i'll erase it
    MEMBER = "member"


class Statuses(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    CANCELLED = "cancelled"
