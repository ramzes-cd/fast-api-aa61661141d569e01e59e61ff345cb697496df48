from typing import List

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.core.exceptions.database_exceptions import (
    CategoryAlreadyExistsException,
    CategoryNotFoundException,
)
from src.infrastructure.sqlite.models.category import Category
from src.schemas.categories import CategoryCreate, CategoryUpdate


class CategoryRepository:
    def get(self, db: Session, skip: int, limit: int) -> List[Category]:
        return db.query(Category).offset(skip).limit(limit).all()

    def get_detail(self, db: Session, category_slug: str) -> Category:
        category = db.query(Category).filter(Category.slug == category_slug).first()
        if not category:
            raise CategoryNotFoundException()
        return category

    def create(self, db: Session, payload: CategoryCreate) -> Category:
        category = Category(**payload.model_dump())
        try:
            db.add(category)
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise CategoryAlreadyExistsException() from exc
        db.refresh(category)
        return category

    def update(self, db: Session, category_slug: str, payload: CategoryUpdate) -> Category:
        category = db.query(Category).filter(Category.slug == category_slug).first()
        if not category:
            raise CategoryNotFoundException()
        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(category, field, value)
        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise CategoryAlreadyExistsException() from exc
        db.refresh(category)
        return category

    def destroy(self, db: Session, category_slug: str) -> None:
        category = db.query(Category).filter(Category.slug == category_slug).first()
        if not category:
            raise CategoryNotFoundException()
        db.delete(category)
        db.commit()
