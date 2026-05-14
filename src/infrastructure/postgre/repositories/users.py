from typing import List

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.database_exceptions import (
    UserByEmailAlreadyExistsException,
    UserByNicknameAlreadyExistsException,
    UserNotFoundException,
)
from src.infrastructure.postgre.models.user import User
from src.schemas.users import UserCreate, UserUpdate


class UserRepository:
    async def get(self, db: AsyncSession, skip: int, limit: int) -> List[User]:
        stmt = select(User).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_detail(self, db: AsyncSession, nickname: str) -> User:
        stmt = select(User).where(User.nickname == nickname)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            raise UserNotFoundException()
        return user

    async def create(self, db: AsyncSession, payload: UserCreate) -> User:
        user = User(**payload.model_dump())
        try:
            db.add(user)
            await db.commit()
        except IntegrityError as exc:
            await db.rollback()
            err = str(exc.orig)
            if "nickname" in err:
                raise UserByNicknameAlreadyExistsException() from exc
            if "email" in err:
                raise UserByEmailAlreadyExistsException() from exc
            raise
        await db.refresh(user)
        return user

    async def update(self, db: AsyncSession, nickname: str, payload: UserUpdate) -> User:
        stmt = select(User).where(User.nickname == nickname)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            raise UserNotFoundException()
        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        try:
            await db.commit()
        except IntegrityError as exc:
            await db.rollback()
            raise UserByEmailAlreadyExistsException() from exc
        await db.refresh(user)
        return user

    async def destroy(self, db: AsyncSession, nickname: str) -> None:
        stmt = select(User).where(User.nickname == nickname)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            raise UserNotFoundException()
        await db.delete(user)
        await db.commit()
