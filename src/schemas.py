from datetime import date, datetime
from pydantic import BaseModel, EmailStr, Field
from pydantic.config import ConfigDict
from typing import Optional

class ContactModel(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    birthday: date
    user_id: int = None
    additional_info: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ContactResponse(BaseModel):
    id: int
    first_name: str = None
    last_name: str = None
    email: str = None
    phone: str = None
    birthday: date = None
    user_id: int = None
    additional_info: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ContactUpdate(ContactModel):
    done: bool

class PasswordReset(BaseModel):
    token: str
    new_password: str

class PasswordResetRequest(BaseModel):
    email: str

class RequestEmail(BaseModel):
    email: EmailStr

class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserModel(BaseModel):
    username: str = Field(min_length=3, max_length=16)
    email: str
    password: str = Field(min_length=6, max_length=15)


class UserDb(BaseModel):
    id: int
    username: str
    email: str
    created_at: Optional[datetime] = None
    avatar: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class UserResponse(BaseModel):
    user: UserDb
    avatar: Optional[str] = None
    detail: str = "User successfully created"
