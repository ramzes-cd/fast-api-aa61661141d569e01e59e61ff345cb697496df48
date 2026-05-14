from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from src.core.exceptions.domain_exceptions import (
    CategoryIsNotUniqueException,
    CategoryNotFoundBySlugException,
)
from src.domain.categories.use_cases.crud_categories import MethodsForCategory
from src.schemas.categories import CategoryCreate, CategoryOut, CategoryUpdate
from src.services.auth import get_current_user

router = APIRouter(prefix="/categories", tags=["categories"], dependencies=[Depends(get_current_user)])


@router.post("/", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
async def create_category(
    payload: CategoryCreate,
    db: AsyncSession = Depends(get_db),
) -> CategoryOut:
    try:
        return await MethodsForCategory().create(db, payload)
    except CategoryIsNotUniqueException as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.get_detail()) from exc


@router.get("/", response_model=List[CategoryOut])
async def list_categories(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)) -> List[CategoryOut]:
    return await MethodsForCategory().get(db, skip, limit)


@router.get("/{category_slug}", response_model=CategoryOut)
async def get_category(category_slug: str, db: AsyncSession = Depends(get_db)) -> CategoryOut:
    try:
        return await MethodsForCategory().get_detail(db, category_slug)
    except CategoryNotFoundBySlugException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.get_detail()) from exc


@router.put("/{category_slug}", response_model=CategoryOut)
async def update_category(
    category_slug: str,
    payload: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
) -> CategoryOut:
    try:
        return await MethodsForCategory().update(db, category_slug, payload)
    except CategoryNotFoundBySlugException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.get_detail()) from exc
    except CategoryIsNotUniqueException as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.get_detail()) from exc


@router.delete("/{category_slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_slug: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    try:
        await MethodsForCategory().destroy(db, category_slug)
    except CategoryNotFoundBySlugException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.get_detail()) from exc
