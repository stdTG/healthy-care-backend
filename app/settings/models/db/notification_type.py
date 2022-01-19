from core.utils.str_enum import StrEnum


class NotificationType(StrEnum):
    push = "push"
    email = "email"
    sms = "sms"
