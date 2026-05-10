from typing import List

from sqlalchemy.orm import Session

from src.core.exceptions.database_exceptions import (
    CommentNotFoundException,
    CredentialException,
    PostNotFoundException,
)
from src.infrastructure.sqlite.models.comment import Comment
from src.infrastructure.sqlite.models.post import Post
from src.schemas.comments import CommentCreate, CommentUpdate


class CommentRepository:
    def get(self, db: Session, post_id: int | None, skip: int, limit: int) -> List[Comment]:
        query = db.query(Comment)
        if post_id is not None:
            post = db.query(Post).filter(Post.id == post_id).first()
            if not post:
                raise PostNotFoundException()
            query = query.filter(Comment.post_id == post_id)
        return query.order_by(Comment.created_at).offset(skip).limit(limit).all()

    def get_detail(self, db: Session, comment_id: int) -> Comment:
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise CommentNotFoundException()
        return comment

    def create(self, db: Session, payload: CommentCreate, author_id: int) -> Comment:
        post = db.query(Post).filter(Post.id == payload.post_id).first()
        if not post:
            raise PostNotFoundException()
        comment = Comment(**payload.model_dump(), author_id=author_id)
        db.add(comment)
        db.commit()
        db.refresh(comment)
        return comment

    def update(self, db: Session, comment_id: int, payload: CommentUpdate, author_id: int) -> Comment:
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise CommentNotFoundException()
        if comment.author_id != author_id:
            raise CredentialException()
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(comment, field, value)
        db.commit()
        db.refresh(comment)
        return comment

    def destroy(self, db: Session, comment_id: int, author_id: int) -> None:
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise CommentNotFoundException()
        if comment.author_id != author_id:
            raise CredentialException()
        db.delete(comment)
        db.commit()
