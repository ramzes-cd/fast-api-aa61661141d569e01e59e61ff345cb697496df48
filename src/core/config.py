from pydantic import SecretStr


class Settings:
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SECRET_AUTH_KEY: SecretStr = SecretStr("change-me-in-production")
    AUTH_ALGORITHM: str = "HS256"


settings = Settings()
