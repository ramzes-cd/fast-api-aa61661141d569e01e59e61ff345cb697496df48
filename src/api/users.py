from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from src.core.exceptions.domain_exceptions import (
    UserEmailIsNotUniqueException,
    UserNicknameIsNotUniqueException,
    UserNotFoundByNicknameException,
)
from src.domain.users.use_cases.crud_users import MethodsForUser
from src.schemas.users import UserCreate, UserOut, UserUpdate
from src.services.auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[UserOut])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: UserOut = Depends(get_current_user),
) -> List[UserOut]:
    return MethodsForUser().get(db, skip, limit)


@router.get("/{nickname}", response_model=UserOut)
def get_user(
    nickname: str,
    db: Session = Depends(get_db),
    _: UserOut = Depends(get_current_user),
) -> UserOut:
    try:
        return MethodsForUser().get_detail(db, nickname)
    except UserNotFoundByNicknameException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.get_detail())


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)) -> UserOut:
    try:
        return MethodsForUser().create(db, payload)
    except UserNicknameIsNotUniqueException as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.get_detail())
    except UserEmailIsNotUniqueException as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.get_detail())


@router.put("/{nickname}", response_model=UserOut)
def update_user(
    nickname: str,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user),
) -> UserOut:
    if current_user.nickname != nickname:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Можно изменять только свой профиль.")
    try:
        return MethodsForUser().update(db, nickname, payload)
    except UserNotFoundByNicknameException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.get_detail())
    except UserEmailIsNotUniqueException as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.get_detail())


@router.delete("/{nickname}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    nickname: str,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user),
) -> None:
    if current_user.nickname != nickname:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Можно удалить только свой профиль.")
    try:
        MethodsForUser().destroy(db, nickname)
    except UserNotFoundByNicknameException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.get_detail())
