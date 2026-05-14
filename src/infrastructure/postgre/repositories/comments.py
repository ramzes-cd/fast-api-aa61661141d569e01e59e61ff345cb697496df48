from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions.database_exceptions import (
    CommentNotFoundException,
    CredentialException,
    PostNotFoundException,
)
from src.infrastructure.postgre.models.comment import Comment
from src.infrastructure.postgre.models.post import Post
from src.schemas.comments import CommentCreate, CommentUpdate


class CommentRepository:
    async def get(self, db: AsyncSession, post_id: int | None, skip: int, limit: int) -> List[Comment]:
        stmt = select(Comment)
        if post_id is not None:
            stmt_post = select(Post).where(Post.id == post_id)
            post_result = await db.execute(stmt_post)
            post = post_result.scalar_one_or_none()
            if not post:
                raise PostNotFoundException()
            stmt = stmt.where(Comment.post_id == post_id)
        stmt = stmt.order_by(Comment.created_at).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_detail(self, db: AsyncSession, comment_id: int) -> Comment:
        stmt = select(Comment).where(Comment.id == comment_id)
        result = await db.execute(stmt)
        comment = result.scalar_one_or_none()
        if not comment:
            raise CommentNotFoundException()
        return comment

    async def create(self, db: AsyncSession, payload: CommentCreate, author_id: int) -> Comment:
        stmt_post = select(Post).where(Post.id == payload.post_id)
        post_result = await db.execute(stmt_post)
        post = post_result.scalar_one_or_none()
        if not post:
            raise PostNotFoundException()
        comment = Comment(**payload.model_dump(), author_id=author_id)
        db.add(comment)
        await db.commit()
        await db.refresh(comment)
        return comment

    async def update(self, db: AsyncSession, comment_id: int, payload: CommentUpdate, author_id: int) -> Comment:
        stmt = select(Comment).where(Comment.id == comment_id)
        result = await db.execute(stmt)
        comment = result.scalar_one_or_none()
        if not comment:
            raise CommentNotFoundException()
        if comment.author_id != author_id:
            raise CredentialException()
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(comment, field, value)
        await db.commit()
        await db.refresh(comment)
        return comment

    async def destroy(self, db: AsyncSession, comment_id: int, author_id: int) -> None:
        stmt = select(Comment).where(Comment.id == comment_id)
        result = await db.execute(stmt)
        comment = result.scalar_one_or_none()
        if not comment:
            raise CommentNotFoundException()
        if comment.author_id != author_id:
            raise CredentialException()
        await db.delete(comment)
        await db.commit()
