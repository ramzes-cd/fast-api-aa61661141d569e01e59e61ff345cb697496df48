from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.database_exceptions import (
    LocationAlreadyExistsException,
    LocationNotFoundException,
)
from src.core.exceptions.domain_exceptions import (
    LocationIsNotUniqueException,
    LocationNotFoundByNameException,
)
from src.infrastructure.postgre.repositories.locations import LocationRepository
from src.schemas.locations import LocationCreate, LocationOut, LocationUpdate


class MethodsForLocation:
    def __init__(self) -> None:
        self._repo = LocationRepository()

    async def get(self, db: AsyncSession, skip: int, limit: int) -> List[LocationOut]:
        items = await self._repo.get(db, skip, limit)
        return [LocationOut.model_validate(item) for item in items]

    async def get_detail(self, db: AsyncSession, name: str) -> LocationOut:
        try:
            location = await self._repo.get_detail(db, name)
        except LocationNotFoundException as exc:
            raise LocationNotFoundByNameException(name) from exc
        return LocationOut.model_validate(location)

    async def create(self, db: AsyncSession, payload: LocationCreate) -> LocationOut:
        try:
            location = await self._repo.create(db, payload)
        except LocationAlreadyExistsException as exc:
            raise LocationIsNotUniqueException(payload.name) from exc
        return LocationOut.model_validate(location)

    async def update(self, db: AsyncSession, name: str, payload: LocationUpdate) -> LocationOut:
        try:
            location = await self._repo.update(db, name, payload)
        except LocationNotFoundException as exc:
            raise LocationNotFoundByNameException(name) from exc
        except LocationAlreadyExistsException as exc:
            raise LocationIsNotUniqueException(payload.name) from exc
        return LocationOut.model_validate(location)

    async def destroy(self, db: AsyncSession, name: str) -> None:
        try:
            await self._repo.destroy(db, name)
        except LocationNotFoundException as exc:
            raise LocationNotFoundByNameException(name) from exc
