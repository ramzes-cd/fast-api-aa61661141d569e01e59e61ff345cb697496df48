from datetime import datetime

from pydantic import BaseModel, field_validator


class LocationBase(BaseModel):
    name: str = None
    is_published: bool = None

    @field_validator("name")
    @staticmethod
    def validate_name(value: str | None):
        if value is None:
            return value
        if len(value) < 5 or len(value) > 40:
            raise ValueError("Название локации должно быть длиной от 5 до 40 символов.")
        return value


class LocationCreate(LocationBase):
    name: str
    is_published: bool = False


class LocationUpdate(LocationBase):
    pass


class LocationOut(LocationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True