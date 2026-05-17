from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.logging import get_logger
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
from src.infrastructure.postgre.repositories.users import UserRepository
from src.resources.auth import get_password_hash
from src.schemas.users import UserCreate, UserOut, UserUpdate

logger = get_logger(__name__)


class MethodsForUser:
    def __init__(self) -> None:
        self._repo = UserRepository()

    async def get(self, db: AsyncSession, skip: int, limit: int) -> List[UserOut]:
        items = await self._repo.get(db, skip, limit)
        return [UserOut.model_validate(item) for item in items]

    async def get_detail(self, db: AsyncSession, nickname: str) -> UserOut:
        try:
            user = await self._repo.get_detail(db, nickname)
        except UserNotFoundException as exc:
            logger.warning("User not found nickname=%s", nickname)
            raise UserNotFoundByNicknameException(nickname) from exc
        return UserOut.model_validate(user)

    async def create(self, db: AsyncSession, payload: UserCreate) -> UserOut:
        payload = payload.model_copy(update={"password": get_password_hash(payload.password)})
        try:
            user = await self._repo.create(db, payload)
        except UserByNicknameAlreadyExistsException as exc:
            raise UserNicknameIsNotUniqueException(payload.nickname) from exc
        except UserByEmailAlreadyExistsException as exc:
            raise UserEmailIsNotUniqueException(payload.email) from exc
        user_out = UserOut.model_validate(user)
        logger.info("User created nickname=%s", user_out.nickname)
        return user_out

    async def update(self, db: AsyncSession, nickname: str, payload: UserUpdate) -> UserOut:
        try:
            user = await self._repo.update(db, nickname, payload)
        except UserNotFoundException as exc:
            logger.warning("User not found for update nickname=%s", nickname)
            raise UserNotFoundByNicknameException(nickname) from exc
        except UserByEmailAlreadyExistsException as exc:
            raise UserEmailIsNotUniqueException(payload.email) from exc
        user_out = UserOut.model_validate(user)
        logger.info("User updated nickname=%s", nickname)
        return user_out

    async def destroy(self, db: AsyncSession, nickname: str) -> None:
        try:
            await self._repo.destroy(db, nickname)
        except UserNotFoundException as exc:
            logger.warning("User not found for delete nickname=%s", nickname)
            raise UserNotFoundByNicknameException(nickname) from exc
        logger.info("User deleted nickname=%s", nickname)
