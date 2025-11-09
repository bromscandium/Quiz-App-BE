import enum


class NotificationStatuses(str, enum.Enum):
    UNREAD = "unread"
    READ = "read"
