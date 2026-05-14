from typing import List

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.database_exceptions import (
    LocationAlreadyExistsException,
    LocationNotFoundException,
)
from src.infrastructure.postgre.models.location import Location
from src.schemas.locations import LocationCreate, LocationUpdate


class LocationRepository:
    async def get(self, db: AsyncSession, skip: int, limit: int) -> List[Location]:
        stmt = select(Location).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_detail(self, db: AsyncSession, name: str) -> Location:
        stmt = select(Location).where(Location.name == name)
        result = await db.execute(stmt)
        location = result.scalar_one_or_none()
        if not location:
            raise LocationNotFoundException()
        return location

    async def create(self, db: AsyncSession, payload: LocationCreate) -> Location:
        location = Location(**payload.model_dump())
        try:
            db.add(location)
            await db.commit()
        except IntegrityError as exc:
            await db.rollback()
            raise LocationAlreadyExistsException() from exc
        await db.refresh(location)
        return location

    async def update(self, db: AsyncSession, name: str, payload: LocationUpdate) -> Location:
        stmt = select(Location).where(Location.name == name)
        result = await db.execute(stmt)
        location = result.scalar_one_or_none()
        if not location:
            raise LocationNotFoundException()
        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(location, field, value)
        try:
            await db.commit()
        except IntegrityError as exc:
            await db.rollback()
            raise LocationAlreadyExistsException() from exc
        await db.refresh(location)
        return location

    async def destroy(self, db: AsyncSession, name: str) -> None:
        stmt = select(Location).where(Location.name == name)
        result = await db.execute(stmt)
        location = result.scalar_one_or_none()
        if not location:
            raise LocationNotFoundException()
        await db.delete(location)
        await db.commit()
