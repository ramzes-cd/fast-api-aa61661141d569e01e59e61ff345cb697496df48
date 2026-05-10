import re
from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator


class UserBase(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    bio_info: str | None = None
    email: EmailStr | None = None


class UserCreate(UserBase):
    nickname: str
    password: str

    @field_validator("nickname")
    @staticmethod
    def validate_nickname(value: str):
        if len(value) < 3 or len(value) > 30:
            raise ValueError("Никнейм должен быть длиной от 3 до 30 символов.")
        if not re.match(r"^[A-Za-z0-9_]+$", value):
            raise ValueError("Никнейм может содержать только латиницу, цифры и _.")
        return value


class UserUpdate(UserBase):
    @field_validator("first_name", "last_name")
    @staticmethod
    def validate_name(value: str | None):
        if value is None:
            return value
        if len(value) < 2 or len(value) > 30:
            raise ValueError("Имя и фамилия должны быть длиной от 2 до 30 символов.")
        if not re.match(r"^[А-Яа-яA-Za-zЁё-]+$", value):
            raise ValueError("Имя и фамилия могут содержать только буквы и дефис.")
        return value


class UserOut(UserBase):
    id: int
    nickname: str
    active: bool
    date_joined: datetime

    class Config:
        from_attributes = True
