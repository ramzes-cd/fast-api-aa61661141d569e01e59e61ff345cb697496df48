from datetime import datetime

from pydantic import BaseModel, field_validator


class CommentBase(BaseModel):
    text: str | None = None

    @field_validator("text")
    @staticmethod
    def validate_text(value: str | None):
        if value is None:
            return value
        if len(value) < 1 or len(value) > 500:
            raise ValueError("Комментарий должен содержать от 1 до 500 символов.")
        return value


class CommentCreate(CommentBase):
    text: str
    post_id: int


class CommentUpdate(CommentBase):
    pass


class CommentOut(CommentCreate):
    id: int
    author_id: int
    created_at: datetime

    class Config:
        from_attributes = True