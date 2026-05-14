from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from src.core.exceptions.domain_exceptions import (
    LocationIsNotUniqueException,
    LocationNotFoundByNameException,
)
from src.domain.locations.use_cases.crud_locations import MethodsForLocation
from src.schemas.locations import LocationCreate, LocationOut, LocationUpdate
from src.services.auth import get_current_user

router = APIRouter(prefix="/locations", tags=["locations"], dependencies=[Depends(get_current_user)])


@router.post("/", response_model=LocationOut, status_code=status.HTTP_201_CREATED)
async def create_location(
    payload: LocationCreate,
    db: AsyncSession = Depends(get_db),
) -> LocationOut:
    try:
        return await MethodsForLocation().create(db, payload)
    except LocationIsNotUniqueException as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.get_detail()) from exc


@router.get("/", response_model=List[LocationOut])
async def list_locations(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)) -> List[LocationOut]:
    return await MethodsForLocation().get(db, skip, limit)


@router.get("/{name}", response_model=LocationOut)
async def get_location(name: str, db: AsyncSession = Depends(get_db)) -> LocationOut:
    try:
        return await MethodsForLocation().get_detail(db, name)
    except LocationNotFoundByNameException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.get_detail()) from exc


@router.put("/{name}", response_model=LocationOut)
async def update_location(
    name: str,
    payload: LocationUpdate,
    db: AsyncSession = Depends(get_db),
) -> LocationOut:
    try:
        return await MethodsForLocation().update(db, name, payload)
    except LocationNotFoundByNameException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.get_detail()) from exc
    except LocationIsNotUniqueException as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.get_detail()) from exc


@router.delete("/{name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_location(
    name: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    try:
        await MethodsForLocation().destroy(db, name)
    except LocationNotFoundByNameException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.get_detail()) from exc
