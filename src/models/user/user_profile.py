from typing import Optional, List

from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    account_id: str

    name: str
    image_url: Optional[str] = Field(default=None)
    language: str = Field(default='en')

    description: Optional[str] = Field(default=None)
    gender: Optional[str] = Field(default=None)
    age: Optional[int] = Field(default=None)
    location: Optional[str] = Field(default=None)

    ethnicity: Optional[str] = Field(default=None)
    nationality: Optional[str] = Field(default=None)

    focus: Optional[List[str]] = Field(default=None)
    social_comfort: Optional[str] = Field(default=None)
    self_confidence: Optional[str] = Field(default=None)

    religion: Optional[str] = Field(default=None)
    politics: Optional[str] = Field(default=None)
    occupation: Optional[str] = Field(default=None)
    education: Optional[str] = Field(default=None)
    income: Optional[str] = Field(default=None)

    body_description: Optional[str] = Field(default=None)
    face_description: Optional[str] = Field(default=None)
    hair_description: Optional[str] = Field(default=None)
    style_description: Optional[str] = Field(default=None)

    pet_preference: Optional[str] = Field(default=None)
    favorite_cuisine: Optional[str] = Field(default=None)
    vacation_destination: Optional[str] = Field(default=None)
    favorite_season: Optional[str] = Field(default=None)
    leisure_activity: Optional[str] = Field(default=None)

    loves: Optional[str] = Field(default=None)
    hates: Optional[str] = Field(default=None)
    hobbies: Optional[str] = Field(default=None)

    parents: Optional[str] = Field(default=None)
    siblings: Optional[str] = Field(default=None)
    spouse: Optional[str] = Field(default=None)
    children: Optional[str] = Field(default=None)
    best_friends: Optional[str] = Field(default=None)
