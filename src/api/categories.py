from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from src.core.exceptions.domain_exceptions import (
    CategoryIsNotUniqueException,
    CategoryNotFoundBySlugException,
)
from src.domain.categories.use_cases.crud_categories import MethodsForCategory
from src.schemas.categories import CategoryCreate, CategoryOut, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("/", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)) -> CategoryOut:
    try:
        return MethodsForCategory().create(db, payload)
    except CategoryIsNotUniqueException as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.get_detail())


@router.get("/", response_model=List[CategoryOut])
def list_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> List[CategoryOut]:
    return MethodsForCategory().get(db, skip, limit)


@router.get("/{category_slug}", response_model=CategoryOut)
def get_category(category_slug: str, db: Session = Depends(get_db)) -> CategoryOut:
    try:
        return MethodsForCategory().get_detail(db, category_slug)
    except CategoryNotFoundBySlugException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.get_detail())


@router.put("/{category_slug}", response_model=CategoryOut)
def update_category(category_slug: str, payload: CategoryUpdate, db: Session = Depends(get_db)) -> CategoryOut:
    try:
        return MethodsForCategory().update(db, category_slug, payload)
    except CategoryNotFoundBySlugException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.get_detail())
    except CategoryIsNotUniqueException as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.get_detail())


@router.delete("/{category_slug}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_slug: str, db: Session = Depends(get_db)) -> None:
    try:
        MethodsForCategory().destroy(db, category_slug)
    except CategoryNotFoundBySlugException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.get_detail())
