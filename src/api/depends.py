from src.domain.auth.use_cases.auth_user import AuthenticateUserUseCase
from src.domain.auth.use_cases.create_access_token import CreateAccessTokenUseCase


def auth_user_use_case() -> AuthenticateUserUseCase:
    return AuthenticateUserUseCase()


def create_access_token_use_case() -> CreateAccessTokenUseCase:
    return CreateAccessTokenUseCase()
