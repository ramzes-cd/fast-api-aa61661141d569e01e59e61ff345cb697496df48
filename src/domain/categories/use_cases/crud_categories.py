from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.logging import get_logger
from src.core.exceptions.database_exceptions import (
    CategoryAlreadyExistsException,
    CategoryNotFoundException,
)
from src.core.exceptions.domain_exceptions import (
    CategoryIsNotUniqueException,
    CategoryNotFoundBySlugException,
)
from src.infrastructure.postgre.repositories.categories import CategoryRepository
from src.schemas.categories import CategoryCreate, CategoryOut, CategoryUpdate

logger = get_logger(__name__)


class MethodsForCategory:
    def __init__(self) -> None:
        self._repo = CategoryRepository()

    async def get(self, db: AsyncSession, skip: int, limit: int) -> List[CategoryOut]:
        items = await self._repo.get(db, skip, limit)
        return [CategoryOut.model_validate(item) for item in items]

    async def get_detail(self, db: AsyncSession, slug: str) -> CategoryOut:
        try:
            category = await self._repo.get_detail(db, slug)
        except CategoryNotFoundException as exc:
            logger.warning("Category not found slug=%s", slug)
            raise CategoryNotFoundBySlugException(slug) from exc
        return CategoryOut.model_validate(category)

    async def create(self, db: AsyncSession, payload: CategoryCreate) -> CategoryOut:
        try:
            category = await self._repo.create(db, payload)
        except CategoryAlreadyExistsException as exc:
            raise CategoryIsNotUniqueException(payload.slug) from exc
        category_out = CategoryOut.model_validate(category)
        logger.info("Category created slug=%s", category_out.slug)
        return category_out

    async def update(self, db: AsyncSession, slug: str, payload: CategoryUpdate) -> CategoryOut:
        try:
            category = await self._repo.update(db, slug, payload)
        except CategoryNotFoundException as exc:
            logger.warning("Category not found for update slug=%s", slug)
            raise CategoryNotFoundBySlugException(slug) from exc
        except CategoryAlreadyExistsException as exc:
            raise CategoryIsNotUniqueException(payload.slug) from exc
        category_out = CategoryOut.model_validate(category)
        logger.info("Category updated slug=%s", slug)
        return category_out

    async def destroy(self, db: AsyncSession, slug: str) -> None:
        try:
            await self._repo.destroy(db, slug)
        except CategoryNotFoundException as exc:
            logger.warning("Category not found for delete slug=%s", slug)
            raise CategoryNotFoundBySlugException(slug) from exc
        logger.info("Category deleted slug=%s", slug)
