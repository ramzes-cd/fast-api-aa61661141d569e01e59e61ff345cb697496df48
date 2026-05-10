from typing import List

from sqlalchemy.orm import Session

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
from src.infrastructure.sqlite.repositories.comments import CommentRepository
from src.schemas.comments import CommentCreate, CommentOut, CommentUpdate


class MethodsForComment:
    def __init__(self) -> None:
        self._repo = CommentRepository()

    def get(self, db: Session, post_id: int | None, skip: int, limit: int) -> List[CommentOut]:
        try:
            comments = self._repo.get(db, post_id, skip, limit)
        except PostNotFoundException as exc:
            raise PostNotFoundByIDException(post_id) from exc
        return [CommentOut.model_validate(item) for item in comments]

    def get_detail(self, db: Session, comment_id: int) -> CommentOut:
        try:
            comment = self._repo.get_detail(db, comment_id)
        except CommentNotFoundException as exc:
            raise CommentNotFoundByIDException(comment_id) from exc
        return CommentOut.model_validate(comment)

    def create(self, db: Session, payload: CommentCreate, author_id: int) -> CommentOut:
        try:
            comment = self._repo.create(db, payload, author_id)
        except PostNotFoundException as exc:
            raise CommentDontCreateException("пост не найден") from exc
        return CommentOut.model_validate(comment)

    def update(self, db: Session, comment_id: int, payload: CommentUpdate, author_id: int) -> CommentOut:
        try:
            comment = self._repo.update(db, comment_id, payload, author_id)
        except CommentNotFoundException as exc:
            raise CommentNotFoundByIDException(comment_id) from exc
        except CredentialException as exc:
            raise CommentDontChangeException("комментарий не принадлежит пользователю") from exc
        return CommentOut.model_validate(comment)

    def destroy(self, db: Session, comment_id: int, author_id: int) -> None:
        try:
            self._repo.destroy(db, comment_id, author_id)
        except CommentNotFoundException as exc:
            raise CommentNotFoundByIDException(comment_id) from exc
        except CredentialException as exc:
            raise CommentDontDestroyException("комментарий не принадлежит пользователю") from exc
