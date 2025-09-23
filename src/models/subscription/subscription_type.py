from enum import Enum

from pydantic import BaseModel, Field


class SubscriptionType(str, Enum):
    NONE = 'none'
    FREE = 'free'
    BASIC = 'basic'
    PREMIUM = 'premium'
    ENTERPRISE = 'enterprise'
    UNLIMITED = 'unlimited'


class Subscribable(BaseModel):
    required_subscription_type: SubscriptionType = Field(default=SubscriptionType.FREE)
