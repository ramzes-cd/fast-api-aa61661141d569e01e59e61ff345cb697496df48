from datetime import datetime, timedelta, timezone

from jose import jwt

from src.core.config import settings


class CreateAccessTokenUseCase:
    def create_token(self, nickname: str, expires_delta: timedelta | None = None) -> str:
        to_encode = {"sub": nickname}
        expire = datetime.now(timezone.utc) + (
            expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        to_encode.update({"exp": expire})
        return jwt.encode(
            claims=to_encode,
            key=settings.SECRET_AUTH_KEY.get_secret_value(),
            algorithm=settings.AUTH_ALGORITHM,
        )
