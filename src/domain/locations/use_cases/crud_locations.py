from typing import List

from sqlalchemy.orm import Session

from src.core.exceptions.database_exceptions import (
    LocationAlreadyExistsException,
    LocationNotFoundException,
)
from src.core.exceptions.domain_exceptions import (
    LocationIsNotUniqueException,
    LocationNotFoundByNameException,
)
from src.infrastructure.sqlite.repositories.locations import LocationRepository
from src.schemas.locations import LocationCreate, LocationOut, LocationUpdate


class MethodsForLocation:
    def __init__(self) -> None:
        self._repo = LocationRepository()

    def get(self, db: Session, skip: int, limit: int) -> List[LocationOut]:
        return [LocationOut.model_validate(item) for item in self._repo.get(db, skip, limit)]

    def get_detail(self, db: Session, name: str) -> LocationOut:
        try:
            location = self._repo.get_detail(db, name)
        except LocationNotFoundException as exc:
            raise LocationNotFoundByNameException(name) from exc
        return LocationOut.model_validate(location)

    def create(self, db: Session, payload: LocationCreate) -> LocationOut:
        try:
            location = self._repo.create(db, payload)
        except LocationAlreadyExistsException as exc:
            raise LocationIsNotUniqueException(payload.name) from exc
        return LocationOut.model_validate(location)

    def update(self, db: Session, name: str, payload: LocationUpdate) -> LocationOut:
        try:
            location = self._repo.update(db, name, payload)
        except LocationNotFoundException as exc:
            raise LocationNotFoundByNameException(name) from exc
        except LocationAlreadyExistsException as exc:
            raise LocationIsNotUniqueException(payload.name) from exc
        return LocationOut.model_validate(location)

    def destroy(self, db: Session, name: str) -> None:
        try:
            self._repo.destroy(db, name)
        except LocationNotFoundException as exc:
            raise LocationNotFoundByNameException(name) from exc
