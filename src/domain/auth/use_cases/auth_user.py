from sqlalchemy.orm import Session

from src.core.exceptions.database_exceptions import UserNotFoundException
from src.core.exceptions.domain_exceptions import UserNotFoundByNicknameException, WrongUserPasswordException
from src.infrastructure.sqlite.repositories.users import UserRepository
from src.resources.auth import verify_password
from src.schemas.users import UserOut


class AuthenticateUserUseCase:
    def __init__(self) -> None:
        self._repo = UserRepository()

    def get_detail(self, database: Session, nickname: str, password: str) -> UserOut:
        try:
            user_model = self._repo.get_detail(database, nickname)
        except UserNotFoundException as exc:
            raise UserNotFoundByNicknameException(nickname) from exc

        if not verify_password(password, user_model.password):
            raise WrongUserPasswordException()

        return UserOut.model_validate(user_model)
