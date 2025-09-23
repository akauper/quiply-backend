from typing import Optional, List

from pydantic import BaseModel, Field
from .user_profile import UserProfile
from src.framework.models import UIDMixin, CreatedAtMixin, UpdatedAtMixin
from .role import UserRole
from ..subscription.subscription_type import SubscriptionType


class AccountData(UIDMixin, CreatedAtMixin, UpdatedAtMixin):
    id: str
    created_at: str
    updated_at: str

    roles: List[UserRole] = Field(default=[UserRole.USER])
    subscription_type: SubscriptionType = Field(default=SubscriptionType.FREE)

    email: str
    first_name: str
    last_name: str
    birthday: str = Field(default='2000-01-01')
    image_url: Optional[str] = Field(default=None)
    phone_number: Optional[str] = Field(default=None)

    receive_account_notifications: bool = Field(default=True)
    receive_newsletter: bool = Field(default=True)
    two_factor_enabled: bool = Field(default=False)
    allow_data_collection: bool = Field(default=True)

    profile: Optional[UserProfile] = Field(default=None)
