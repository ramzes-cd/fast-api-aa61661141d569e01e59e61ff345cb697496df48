from typing import List

from sqlalchemy.orm import Session

from src.core.exceptions.database_exceptions import (
    CategoryNotFoundException,
    CredentialException,
    LocationNotFoundException,
    PostNotFoundException,
    UserNotFoundException,
)
from src.core.exceptions.domain_exceptions import (
    PostDontChangeException,
    PostDontCreateException,
    PostDontDestroyException,
    PostNotFoundByIDException,
)
from src.infrastructure.sqlite.repositories.posts import PostRepository
from src.schemas.posts import PostCreate, PostDetail, PostOut, PostUpdate


class MethodsForPost:
    def __init__(self) -> None:
        self._repo = PostRepository()

    def get(self, db: Session, skip: int, limit: int, published_only: bool) -> List[PostOut]:
        return [PostOut.model_validate(item) for item in self._repo.get(db, skip, limit, published_only)]

    def get_detail(self, db: Session, post_id: int) -> PostDetail:
        try:
            post = self._repo.get_detail(db, post_id)
        except PostNotFoundException as exc:
            raise PostNotFoundByIDException(post_id) from exc
        return PostDetail.model_validate(post)

    def create(self, db: Session, payload: PostCreate, nickname: str) -> PostOut:
        try:
            post = self._repo.create(db, payload, nickname)
        except UserNotFoundException as exc:
            raise PostDontCreateException("автор не найден") from exc
        except CategoryNotFoundException as exc:
            raise PostDontCreateException("категория не найдена") from exc
        except LocationNotFoundException as exc:
            raise PostDontCreateException("локация не найдена") from exc
        return PostOut.model_validate(post)

    def update(self, db: Session, payload: PostUpdate, post_id: int, author_id: int) -> PostOut:
        try:
            post = self._repo.update(db, payload, post_id, author_id)
        except PostNotFoundException as exc:
            raise PostNotFoundByIDException(post_id) from exc
        except CategoryNotFoundException as exc:
            raise PostDontChangeException("категория не найдена") from exc
        except LocationNotFoundException as exc:
            raise PostDontChangeException("локация не найдена") from exc
        except CredentialException as exc:
            raise PostDontChangeException("пост не принадлежит пользователю") from exc
        return PostOut.model_validate(post)

    def destroy(self, db: Session, post_id: int, author_id: int) -> None:
        try:
            self._repo.destroy(db, post_id, author_id)
        except PostNotFoundException as exc:
            raise PostNotFoundByIDException(post_id) from exc
        except CredentialException as exc:
            raise PostDontDestroyException("пост не принадлежит пользователю") from exc
