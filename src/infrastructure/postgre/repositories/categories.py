from typing import List

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.database_exceptions import (
    CategoryAlreadyExistsException,
    CategoryNotFoundException,
)
from src.infrastructure.postgre.models.category import Category
from src.schemas.categories import CategoryCreate, CategoryUpdate


class CategoryRepository:
    async def get(self, db: AsyncSession, skip: int, limit: int) -> List[Category]:
        stmt = select(Category).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_detail(self, db: AsyncSession, category_slug: str) -> Category:
        stmt = select(Category).where(Category.slug == category_slug)
        result = await db.execute(stmt)
        category = result.scalar_one_or_none()
        if not category:
            raise CategoryNotFoundException()
        return category

    async def create(self, db: AsyncSession, payload: CategoryCreate) -> Category:
        category = Category(**payload.model_dump())
        try:
            db.add(category)
            await db.commit()
        except IntegrityError as exc:
            await db.rollback()
            raise CategoryAlreadyExistsException() from exc
        await db.refresh(category)
        return category

    async def update(self, db: AsyncSession, category_slug: str, payload: CategoryUpdate) -> Category:
        stmt = select(Category).where(Category.slug == category_slug)
        result = await db.execute(stmt)
        category = result.scalar_one_or_none()
        if not category:
            raise CategoryNotFoundException()
        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(category, field, value)
        try:
            await db.commit()
        except IntegrityError as exc:
            await db.rollback()
            raise CategoryAlreadyExistsException() from exc
        await db.refresh(category)
        return category

    async def destroy(self, db: AsyncSession, category_slug: str) -> None:
        stmt = select(Category).where(Category.slug == category_slug)
        result = await db.execute(stmt)
        category = result.scalar_one_or_none()
        if not category:
            raise CategoryNotFoundException()
        await db.delete(category)
        await db.commit()
