from typing import Optional, List

from pydantic import Field, BaseModel
from .base import SerializableObject


class UserProfile(BaseModel):
    image_url: str = Field(default='')
    name: str = Field(default='')
    language: str = Field(default='')

    gender: str = Field(default='')
    age: str = Field(default='')
    ethnicity: str = Field(default='')
    nationality: str = Field(default='')
    location: str = Field(default='')

    focus: List[str] = Field(default_factory=list)
    social_comfort: str = Field(default='')
    self_confidence: str = Field(default='')

    religion: str = Field(default='')
    politics: str = Field(default='')
    occupation: str = Field(default='')
    education: str = Field(default='')
    income: str = Field(default='')

    body_description: str = Field(default='')
    face_description: str = Field(default='')
    hair_description: str = Field(default='')
    style_description: str = Field(default='')

    pet_preference: str = Field(default='')
    favorite_cuisine: str = Field(default='')
    vacation_destination: str = Field(default='')
    favorite_season: str = Field(default='')
    leisure_activity: str = Field(default='')

    loves: str = Field(default='')
    hates: str = Field(default='')
    hobbies: str = Field(default='')

    parents: str = Field(default='')
    siblings: str = Field(default='')
    spouse: str = Field(default='')
    children: str = Field(default='')
    best_friends: str = Field(default='')

    description: str = Field(default='')


class QuiplyUser(SerializableObject):
    uid: str

    email: str = Field(description="Email of the user")
    phone_number: Optional[str] = Field(default=None, description="Phone number of the user")
    first_name: str = Field(description="First name of the user")
    last_name: str = Field(description="Last name of the user")
    birthday: str = Field(description="Birthday of the user in ISO format")
    account_image_url: Optional[str] = Field(default=None, description="Image URL of the user's ACCOUNT")

    profile: UserProfile = Field(default_factory=UserProfile, description="Profile of the user")
