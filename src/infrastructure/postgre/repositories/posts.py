from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.core.exceptions.database_exceptions import (
    CategoryNotFoundException,
    CredentialException,
    LocationNotFoundException,
    PostNotFoundException,
    UserNotFoundException,
)
from src.infrastructure.postgre.models.category import Category
from src.infrastructure.postgre.models.location import Location
from src.infrastructure.postgre.models.post import Post
from src.infrastructure.postgre.models.user import User
from src.schemas.posts import PostCreate, PostUpdate


class PostRepository:
    async def get(self, db: AsyncSession, skip: int, limit: int, published_only: bool) -> List[Post]:
        stmt = select(Post)
        if published_only:
            stmt = stmt.where(Post.is_published.is_(True))
        stmt = stmt.order_by(Post.pub_date.desc()).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_detail(self, db: AsyncSession, post_id: int) -> Post:
        stmt = (
            select(Post)
            .options(
                joinedload(Post.author),
                joinedload(Post.category),
                joinedload(Post.location),
                joinedload(Post.comments),
            )
            .where(Post.id == post_id)
        )
        result = await db.execute(stmt)
        post = result.unique().scalar_one_or_none()
        if not post:
            raise PostNotFoundException()
        return post

    async def create(self, db: AsyncSession, payload: PostCreate, nickname: str) -> Post:
        stmt_user = select(User).where(User.nickname == nickname)
        user_result = await db.execute(stmt_user)
        author = user_result.scalar_one_or_none()
        if not author:
            raise UserNotFoundException()

        stmt_cat = select(Category).where(Category.slug == payload.category_slug)
        cat_result = await db.execute(stmt_cat)
        category = cat_result.scalar_one_or_none()
        if not category:
            raise CategoryNotFoundException()

        stmt_loc = select(Location).where(Location.name == payload.location_name)
        loc_result = await db.execute(stmt_loc)
        location = loc_result.scalar_one_or_none()
        if not location:
            raise LocationNotFoundException()

        data = payload.model_dump(exclude={"location_name", "category_slug", "author_id"})
        data.update({"author_id": author.id, "location_id": location.id, "category_id": category.id})
        post = Post(**data)
        db.add(post)
        await db.commit()
        await db.refresh(post)
        return post

    async def update(self, db: AsyncSession, payload: PostUpdate, post_id: int, author_id: int) -> Post:
        stmt_post = select(Post).where(Post.id == post_id)
        post_result = await db.execute(stmt_post)
        post = post_result.scalar_one_or_none()
        if not post:
            raise PostNotFoundException()
        if post.author_id != author_id:
            raise CredentialException()

        stmt_cat = select(Category).where(Category.slug == payload.category_slug)
        cat_result = await db.execute(stmt_cat)
        category = cat_result.scalar_one_or_none()
        if not category:
            raise CategoryNotFoundException()

        stmt_loc = select(Location).where(Location.name == payload.location_name)
        loc_result = await db.execute(stmt_loc)
        location = loc_result.scalar_one_or_none()
        if not location:
            raise LocationNotFoundException()

        data = payload.model_dump(exclude={"location_name", "category_slug", "author_id"}, exclude_unset=True)
        data.update({"location_id": location.id, "category_id": category.id})
        for field, value in data.items():
            setattr(post, field, value)
        await db.commit()
        await db.refresh(post)
        return post

    async def destroy(self, db: AsyncSession, post_id: int, author_id: int) -> None:
        stmt_post = select(Post).where(Post.id == post_id)
        post_result = await db.execute(stmt_post)
        post = post_result.scalar_one_or_none()
        if not post:
            raise PostNotFoundException()
        if post.author_id != author_id:
            raise CredentialException()
        await db.delete(post)
        await db.commit()
