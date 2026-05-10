from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from src.core.exceptions.domain_exceptions import (
    LocationIsNotUniqueException,
    LocationNotFoundByNameException,
)
from src.domain.locations.use_cases.crud_locations import MethodsForLocation
from src.schemas.locations import LocationCreate, LocationOut, LocationUpdate

router = APIRouter(prefix="/locations", tags=["locations"])


@router.post("/", response_model=LocationOut, status_code=status.HTTP_201_CREATED)
def create_location(payload: LocationCreate, db: Session = Depends(get_db)) -> LocationOut:
    try:
        return MethodsForLocation().create(db, payload)
    except LocationIsNotUniqueException as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.get_detail())


@router.get("/", response_model=List[LocationOut])
def list_locations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> List[LocationOut]:
    return MethodsForLocation().get(db, skip, limit)


@router.get("/{name}", response_model=LocationOut)
def get_location(name: str, db: Session = Depends(get_db)) -> LocationOut:
    try:
        return MethodsForLocation().get_detail(db, name)
    except LocationNotFoundByNameException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.get_detail())


@router.put("/{name}", response_model=LocationOut)
def update_location(name: str, payload: LocationUpdate, db: Session = Depends(get_db)) -> LocationOut:
    try:
        return MethodsForLocation().update(db, name, payload)
    except LocationNotFoundByNameException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.get_detail())
    except LocationIsNotUniqueException as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.get_detail())


@router.delete("/{name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_location(name: str, db: Session = Depends(get_db)) -> None:
    try:
        MethodsForLocation().destroy(db, name)
    except LocationNotFoundByNameException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.get_detail())
