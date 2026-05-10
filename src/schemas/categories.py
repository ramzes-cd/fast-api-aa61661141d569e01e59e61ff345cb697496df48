from datetime import datetime

from pydantic import BaseModel, field_validator


class CategoryBase(BaseModel):
    slug: str = None
    title: str = None
    description: str = None
    is_published: bool = None

    @field_validator("slug")
    @staticmethod
    def validate_slug(value: str | None):
        if value is None:
            return value
        if len(value) < 5 or len(value) > 40:
            raise ValueError("Slug должен быть длиной от 5 до 40 символов.")
        return value


class CategoryCreate(CategoryBase):
    slug: str
    title: str
    description: str | None = None
    is_published: bool = False


class CategoryUpdate(CategoryBase):
    pass


class CategoryOut(CategoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True