from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str = Field(description="Токен доступа к системе.")
    token_type: str = Field(description="Тип токена.")
