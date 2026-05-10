from typing import List

from sqlalchemy.orm import Session, joinedload

from src.core.exceptions.database_exceptions import (
    CategoryNotFoundException,
    CredentialException,
    LocationNotFoundException,
    PostNotFoundException,
    UserNotFoundException,
)
from src.infrastructure.sqlite.models.category import Category
from src.infrastructure.sqlite.models.location import Location
from src.infrastructure.sqlite.models.post import Post
from src.infrastructure.sqlite.models.user import User
from src.schemas.posts import PostCreate, PostUpdate


class PostRepository:
    def get(self, db: Session, skip: int, limit: int, published_only: bool) -> List[Post]:
        query = db.query(Post)
        if published_only:
            query = query.filter(Post.is_published.is_(True))
        return query.order_by(Post.pub_date.desc()).offset(skip).limit(limit).all()

    def get_detail(self, db: Session, post_id: int) -> Post:
        post = (
            db.query(Post)
            .options(
                joinedload(Post.author),
                joinedload(Post.category),
                joinedload(Post.location),
                joinedload(Post.comments),
            )
            .filter(Post.id == post_id)
            .first()
        )
        if not post:
            raise PostNotFoundException()
        return post

    def create(self, db: Session, payload: PostCreate, nickname: str) -> Post:
        author = db.query(User).filter(User.nickname == nickname).first()
        if not author:
            raise UserNotFoundException()

        category = db.query(Category).filter(Category.slug == payload.category_slug).first()
        if not category:
            raise CategoryNotFoundException()

        location = db.query(Location).filter(Location.name == payload.location_name).first()
        if not location:
            raise LocationNotFoundException()

        data = payload.model_dump(exclude={"location_name", "category_slug", "author_id"})
        data.update({"author_id": author.id, "location_id": location.id, "category_id": category.id})
        post = Post(**data)
        db.add(post)
        db.commit()
        db.refresh(post)
        return post

    def update(self, db: Session, payload: PostUpdate, post_id: int, author_id: int) -> Post:
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise PostNotFoundException()
        if post.author_id != author_id:
            raise CredentialException()

        category = db.query(Category).filter(Category.slug == payload.category_slug).first()
        if not category:
            raise CategoryNotFoundException()

        location = db.query(Location).filter(Location.name == payload.location_name).first()
        if not location:
            raise LocationNotFoundException()

        data = payload.model_dump(exclude={"location_name", "category_slug", "author_id"}, exclude_unset=True)
        data.update({"location_id": location.id, "category_id": category.id})
        for field, value in data.items():
            setattr(post, field, value)
        db.commit()
        db.refresh(post)
        return post

    def destroy(self, db: Session, post_id: int, author_id: int) -> None:
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise PostNotFoundException()
        if post.author_id != author_id:
            raise CredentialException()
        db.delete(post)
        db.commit()
