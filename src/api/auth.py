from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from src.api.depends import auth_user_use_case, create_access_token_use_case
from src.core.exceptions.domain_exceptions import UserNotFoundByNicknameException, WrongUserPasswordException
from src.domain.auth.use_cases.auth_user import AuthenticateUserUseCase
from src.domain.auth.use_cases.create_access_token import CreateAccessTokenUseCase
from src.schemas.auth import Token

router = APIRouter(tags=["auth"])


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_use_case: AuthenticateUserUseCase = Depends(auth_user_use_case),
    create_token_use_case: CreateAccessTokenUseCase = Depends(create_access_token_use_case),
    db: AsyncSession = Depends(get_db),
) -> Token:
    try:
        user = await auth_use_case.get_detail(db, form_data.username, form_data.password)
    except WrongUserPasswordException as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=exc.get_detail(),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except UserNotFoundByNicknameException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.get_detail()) from exc

    access_token = create_token_use_case.create_token(user.nickname)
    return Token(access_token=access_token, token_type="bearer")
