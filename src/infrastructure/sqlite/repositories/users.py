from typing import List

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.core.exceptions.database_exceptions import (
    UserByEmailAlreadyExistsException,
    UserByNicknameAlreadyExistsException,
    UserNotFoundException,
)
from src.infrastructure.sqlite.models.user import User
from src.schemas.users import UserCreate, UserUpdate


class UserRepository:
    def get(self, db: Session, skip: int, limit: int) -> List[User]:
        return db.query(User).offset(skip).limit(limit).all()

    def get_detail(self, db: Session, nickname: str) -> User:
        user = db.query(User).filter(User.nickname == nickname).first()
        if not user:
            raise UserNotFoundException()
        return user

    def create(self, db: Session, payload: UserCreate) -> User:
        user = User(**payload.model_dump())
        try:
            db.add(user)
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            err = str(exc.orig)
            if "nickname" in err:
                raise UserByNicknameAlreadyExistsException() from exc
            if "email" in err:
                raise UserByEmailAlreadyExistsException() from exc
            raise
        db.refresh(user)
        return user

    def update(self, db: Session, nickname: str, payload: UserUpdate) -> User:
        user = db.query(User).filter(User.nickname == nickname).first()
        if not user:
            raise UserNotFoundException()
        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise UserByEmailAlreadyExistsException() from exc
        db.refresh(user)
        return user

    def destroy(self, db: Session, nickname: str) -> None:
        user = db.query(User).filter(User.nickname == nickname).first()
        if not user:
            raise UserNotFoundException()
        db.delete(user)
        db.commit()
