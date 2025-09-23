from typing import Optional, Any, Dict

from pydantic import BaseModel, Field


class CreateAccountDataRequest(BaseModel):
    id: str
    created_at: str

    email: str
    first_name: str
    last_name: str
    birthday: str
    image_url: Optional[str] = Field(default=None)
    phone_number: Optional[str] = Field(default=None)


class UpdateAccountDataRequest(BaseModel):
    user_id: str
    updated_fields: Dict[str, Any]


class UpdateAccountNameRequest(BaseModel):
    uid: str
    first_name: Optional[str] = Field(default=None)
    last_name: Optional[str] = Field(default=None)


class UpdateUserProfileRequest(BaseModel):
    user_id: str
    updated_fields: Dict[str, Any]
