from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, field_validator

from src.schemas.users import UserOut
from src.schemas.categories import CategoryOut
from src.schemas.locations import LocationOut
from src.schemas.comments import CommentOut


class PostBase(BaseModel):
    title: str | None = None
    text: str | None = None
    pub_date: datetime | None = None
    is_published: bool | None = None
    image: str | None = None
    location_id: int | None = None
    category_id: int | None = None

    @field_validator("title")
    @staticmethod
    def validate_title(value: str | None):
        if value is None:
            return value
        if len(value) < 5 or len(value) > 120:
            raise ValueError("Заголовок должен быть длиной от 5 до 120 символов.")
        return value

    @field_validator("text")
    @staticmethod
    def validate_text(value: str | None):
        if value is None:
            return value
        if len(value.strip()) == 0:
            raise ValueError("Текст поста не может быть пустым.")
        return value


class PostCreate(PostBase):
    title: str
    text: str
    pub_date: datetime
    author_id: int | None = None  # Можно убрать, если будем брать из текущего пользователя
    location_name: str
    category_slug: str


class PostUpdate(PostBase):
    location_name: str
    category_slug: str


class PostOut(PostBase):
    id: int
    created_at: datetime
    author_id: int
    location_id: int | None = None
    category_id: int | None = None

    class Config:
        from_attributes = True


class PostDetail(PostOut):
    author: UserOut
    category: Optional[CategoryOut] = None
    location: Optional[LocationOut] = None
    comments: List[CommentOut] = []

    class Config:
        from_attributes = True