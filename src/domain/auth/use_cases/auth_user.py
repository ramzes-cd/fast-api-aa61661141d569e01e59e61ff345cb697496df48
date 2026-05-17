from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.database_exceptions import UserNotFoundException
from src.core.logging import get_logger
from src.core.exceptions.domain_exceptions import UserNotFoundByNicknameException, WrongUserPasswordException
from src.infrastructure.postgre.repositories.users import UserRepository
from src.resources.auth import verify_password
from src.schemas.users import UserOut


logger = get_logger(__name__)


class AuthenticateUserUseCase:
    def __init__(self) -> None:
        self._repo = UserRepository()

    async def get_detail(self, database: AsyncSession, nickname: str, password: str) -> UserOut:
        try:
            user_model = await self._repo.get_detail(database, nickname)
        except UserNotFoundException as exc:
            logger.warning("Authentication failed: user not found nickname=%s", nickname)
            raise UserNotFoundByNicknameException(nickname) from exc

        if not verify_password(password, user_model.password):
            logger.warning("Authentication failed: wrong password nickname=%s", nickname)
            raise WrongUserPasswordException()

        logger.info("User authenticated nickname=%s", nickname)
        return UserOut.model_validate(user_model)
