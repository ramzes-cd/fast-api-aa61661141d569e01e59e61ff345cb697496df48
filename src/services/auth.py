from fastapi import Depends
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from src.core.config import settings
from src.core.exceptions.auth_exceptions import CredentialsException
from src.core.exceptions.database_exceptions import UserNotFoundException
from src.infrastructure.sqlite.database import get_db
from src.infrastructure.sqlite.repositories.users import UserRepository
from src.resources.auth import oauth2_scheme
from src.schemas.users import UserOut


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> UserOut:
    auth_error_message = "Данные авторизации не удалось проверить."

    try:
        payload = jwt.decode(
            token=token,
            key=settings.SECRET_AUTH_KEY.get_secret_value(),
            algorithms=[settings.AUTH_ALGORITHM],
        )
        nickname: str | None = payload.get("sub")
        if nickname is None:
            raise CredentialsException(detail=auth_error_message)
    except JWTError as exc:
        raise CredentialsException(detail=auth_error_message) from exc

    try:
        user = UserRepository().get_detail(db, nickname)
    except UserNotFoundException as exc:
        raise CredentialsException(detail=auth_error_message) from exc

    return UserOut.model_validate(user)
