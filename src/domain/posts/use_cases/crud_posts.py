from pathlib import Path
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

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
from src.infrastructure.postgre.repositories.posts import PostRepository
from src.schemas.posts import PostCreate, PostDetail, PostOut, PostUpdate


def _media_path_to_disk(image_url: str | None) -> Path | None:
    if not image_url:
        return None
    relative = str(image_url).replace("/media/", "uploads/").lstrip("/")
    return Path(relative)


class MethodsForPost:
    def __init__(self) -> None:
        self._repo = PostRepository()

    async def get(self, db: AsyncSession, skip: int, limit: int, published_only: bool) -> List[PostOut]:
        rows = await self._repo.get(db, skip, limit, published_only)
        return [PostOut.model_validate(item) for item in rows]

    async def get_detail(self, db: AsyncSession, post_id: int) -> PostDetail:
        try:
            post = await self._repo.get_detail(db, post_id)
        except PostNotFoundException as exc:
            raise PostNotFoundByIDException(post_id) from exc
        return PostDetail.model_validate(post)

    async def create(self, db: AsyncSession, payload: PostCreate, nickname: str) -> PostOut:
        try:
            post = await self._repo.create(db, payload, nickname)
        except UserNotFoundException as exc:
            raise PostDontCreateException("автор не найден") from exc
        except CategoryNotFoundException as exc:
            raise PostDontCreateException("категория не найдена") from exc
        except LocationNotFoundException as exc:
            raise PostDontCreateException("локация не найдена") from exc
        return PostOut.model_validate(post)

    async def update(self, db: AsyncSession, payload: PostUpdate, post_id: int, author_id: int) -> PostOut:
        try:
            post = await self._repo.update(db, payload, post_id, author_id)
        except PostNotFoundException as exc:
            raise PostNotFoundByIDException(post_id) from exc
        except CategoryNotFoundException as exc:
            raise PostDontChangeException("категория не найдена") from exc
        except LocationNotFoundException as exc:
            raise PostDontChangeException("локация не найдена") from exc
        except CredentialException as exc:
            raise PostDontChangeException("пост не принадлежит пользователю") from exc
        return PostOut.model_validate(post)

    async def destroy(self, db: AsyncSession, post_id: int, author_id: int) -> None:
        try:
            post = await self._repo.get_detail(db, post_id)
            image = post.image
            await self._repo.destroy(db, post_id, author_id)
            path = _media_path_to_disk(image)
            if path is not None and path.is_file():
                path.unlink()
        except PostNotFoundException as exc:
            raise PostNotFoundByIDException(post_id) from exc
        except CredentialException as exc:
            raise PostDontDestroyException("пост не принадлежит пользователю") from exc
