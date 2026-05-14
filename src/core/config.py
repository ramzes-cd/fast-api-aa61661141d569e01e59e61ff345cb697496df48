from urllib.parse import quote_plus

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "blogicum"
    POSTGRES_USER: SecretStr = SecretStr("blogicum_user")
    POSTGRES_PASSWORD: SecretStr = SecretStr("blogicum_password")

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SECRET_AUTH_KEY: SecretStr = SecretStr("change-me-in-production")
    AUTH_ALGORITHM: str = "HS256"

    @property
    def postgres_url(self) -> str:
        user = quote_plus(self.POSTGRES_USER.get_secret_value())
        password = quote_plus(self.POSTGRES_PASSWORD.get_secret_value())
        return (
            f"postgresql+asyncpg://{user}:{password}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()
