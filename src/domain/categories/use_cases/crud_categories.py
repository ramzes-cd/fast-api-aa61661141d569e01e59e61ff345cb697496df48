from typing import List

from sqlalchemy.orm import Session

from src.core.exceptions.database_exceptions import (
    CategoryAlreadyExistsException,
    CategoryNotFoundException,
)
from src.core.exceptions.domain_exceptions import (
    CategoryIsNotUniqueException,
    CategoryNotFoundBySlugException,
)
from src.infrastructure.sqlite.repositories.categories import CategoryRepository
from src.schemas.categories import CategoryCreate, CategoryOut, CategoryUpdate


class MethodsForCategory:
    def __init__(self) -> None:
        self._repo = CategoryRepository()

    def get(self, db: Session, skip: int, limit: int) -> List[CategoryOut]:
        return [CategoryOut.model_validate(item) for item in self._repo.get(db, skip, limit)]

    def get_detail(self, db: Session, slug: str) -> CategoryOut:
        try:
            category = self._repo.get_detail(db, slug)
        except CategoryNotFoundException as exc:
            raise CategoryNotFoundBySlugException(slug) from exc
        return CategoryOut.model_validate(category)

    def create(self, db: Session, payload: CategoryCreate) -> CategoryOut:
        try:
            category = self._repo.create(db, payload)
        except CategoryAlreadyExistsException as exc:
            raise CategoryIsNotUniqueException(payload.slug) from exc
        return CategoryOut.model_validate(category)

    def update(self, db: Session, slug: str, payload: CategoryUpdate) -> CategoryOut:
        try:
            category = self._repo.update(db, slug, payload)
        except CategoryNotFoundException as exc:
            raise CategoryNotFoundBySlugException(slug) from exc
        except CategoryAlreadyExistsException as exc:
            raise CategoryIsNotUniqueException(payload.slug) from exc
        return CategoryOut.model_validate(category)

    def destroy(self, db: Session, slug: str) -> None:
        try:
            self._repo.destroy(db, slug)
        except CategoryNotFoundException as exc:
            raise CategoryNotFoundBySlugException(slug) from exc
