from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    WAITLIST_USER = "waitlist_user"
    INVESTOR = 'investor'
