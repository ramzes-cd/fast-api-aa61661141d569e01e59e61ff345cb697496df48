from typing import List

from sqlalchemy.orm import Session

from src.core.exceptions.database_exceptions import (
    UserByEmailAlreadyExistsException,
    UserByNicknameAlreadyExistsException,
    UserNotFoundException,
)
from src.core.exceptions.domain_exceptions import (
    UserEmailIsNotUniqueException,
    UserNicknameIsNotUniqueException,
    UserNotFoundByNicknameException,
)
from src.infrastructure.sqlite.repositories.users import UserRepository
from src.resources.auth import get_password_hash
from src.schemas.users import UserCreate, UserOut, UserUpdate


class MethodsForUser:
    def __init__(self) -> None:
        self._repo = UserRepository()

    def get(self, db: Session, skip: int, limit: int) -> List[UserOut]:
        return [UserOut.model_validate(item) for item in self._repo.get(db, skip, limit)]

    def get_detail(self, db: Session, nickname: str) -> UserOut:
        try:
            user = self._repo.get_detail(db, nickname)
        except UserNotFoundException as exc:
            raise UserNotFoundByNicknameException(nickname) from exc
        return UserOut.model_validate(user)

    def create(self, db: Session, payload: UserCreate) -> UserOut:
        payload = payload.model_copy(update={"password": get_password_hash(payload.password)})
        try:
            user = self._repo.create(db, payload)
        except UserByNicknameAlreadyExistsException as exc:
            raise UserNicknameIsNotUniqueException(payload.nickname) from exc
        except UserByEmailAlreadyExistsException as exc:
            raise UserEmailIsNotUniqueException(payload.email) from exc
        return UserOut.model_validate(user)

    def update(self, db: Session, nickname: str, payload: UserUpdate) -> UserOut:
        try:
            user = self._repo.update(db, nickname, payload)
        except UserNotFoundException as exc:
            raise UserNotFoundByNicknameException(nickname) from exc
        except UserByEmailAlreadyExistsException as exc:
            raise UserEmailIsNotUniqueException(payload.email) from exc
        return UserOut.model_validate(user)

    def destroy(self, db: Session, nickname: str) -> None:
        try:
            self._repo.destroy(db, nickname)
        except UserNotFoundException as exc:
            raise UserNotFoundByNicknameException(nickname) from exc
