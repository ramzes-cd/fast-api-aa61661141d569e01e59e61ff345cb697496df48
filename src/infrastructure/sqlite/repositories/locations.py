from typing import List

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.core.exceptions.database_exceptions import (
    LocationAlreadyExistsException,
    LocationNotFoundException,
)
from src.infrastructure.sqlite.models.location import Location
from src.schemas.locations import LocationCreate, LocationUpdate


class LocationRepository:
    def get(self, db: Session, skip: int, limit: int) -> List[Location]:
        return db.query(Location).offset(skip).limit(limit).all()

    def get_detail(self, db: Session, name: str) -> Location:
        location = db.query(Location).filter(Location.name == name).first()
        if not location:
            raise LocationNotFoundException()
        return location

    def create(self, db: Session, payload: LocationCreate) -> Location:
        location = Location(**payload.model_dump())
        try:
            db.add(location)
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise LocationAlreadyExistsException() from exc
        db.refresh(location)
        return location

    def update(self, db: Session, name: str, payload: LocationUpdate) -> Location:
        location = db.query(Location).filter(Location.name == name).first()
        if not location:
            raise LocationNotFoundException()
        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(location, field, value)
        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise LocationAlreadyExistsException() from exc
        db.refresh(location)
        return location

    def destroy(self, db: Session, name: str) -> None:
        location = db.query(Location).filter(Location.name == name).first()
        if not location:
            raise LocationNotFoundException()
        db.delete(location)
        db.commit()
