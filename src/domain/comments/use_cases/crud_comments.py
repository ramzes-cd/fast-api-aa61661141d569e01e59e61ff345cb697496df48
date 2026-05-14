from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.database_exceptions import (
    CommentNotFoundException,
    CredentialException,
    PostNotFoundException,
)
from src.core.exceptions.domain_exceptions import (
    CommentDontChangeException,
    CommentDontCreateException,
    CommentDontDestroyException,
    CommentNotFoundByIDException,
    PostNotFoundByIDException,
)
from src.infrastructure.postgre.repositories.comments import CommentRepository
from src.schemas.comments import CommentCreate, CommentOut, CommentUpdate


class MethodsForComment:
    def __init__(self) -> None:
        self._repo = CommentRepository()

    async def get(self, db: AsyncSession, post_id: int | None, skip: int, limit: int) -> List[CommentOut]:
        try:
            comments = await self._repo.get(db, post_id, skip, limit)
        except PostNotFoundException as exc:
            raise PostNotFoundByIDException(post_id) from exc
        return [CommentOut.model_validate(item) for item in comments]

    async def get_detail(self, db: AsyncSession, comment_id: int) -> CommentOut:
        try:
            comment = await self._repo.get_detail(db, comment_id)
        except CommentNotFoundException as exc:
            raise CommentNotFoundByIDException(comment_id) from exc
        return CommentOut.model_validate(comment)

    async def create(self, db: AsyncSession, payload: CommentCreate, author_id: int) -> CommentOut:
        try:
            comment = await self._repo.create(db, payload, author_id)
        except PostNotFoundException as exc:
            raise CommentDontCreateException("пост не найден") from exc
        return CommentOut.model_validate(comment)

    async def update(self, db: AsyncSession, comment_id: int, payload: CommentUpdate, author_id: int) -> CommentOut:
        try:
            comment = await self._repo.update(db, comment_id, payload, author_id)
        except CommentNotFoundException as exc:
            raise CommentNotFoundByIDException(comment_id) from exc
        except CredentialException as exc:
            raise CommentDontChangeException("комментарий не принадлежит пользователю") from exc
        return CommentOut.model_validate(comment)

    async def destroy(self, db: AsyncSession, comment_id: int, author_id: int) -> None:
        try:
            await self._repo.destroy(db, comment_id, author_id)
        except CommentNotFoundException as exc:
            raise CommentNotFoundByIDException(comment_id) from exc
        except CredentialException as exc:
            raise CommentDontDestroyException("комментарий не принадлежит пользователю") from exc
