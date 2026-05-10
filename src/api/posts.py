from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from src.core.exceptions.domain_exceptions import (
    PostDontChangeException,
    PostDontCreateException,
    PostDontDestroyException,
    PostNotFoundByIDException,
)
from src.domain.posts.use_cases.crud_posts import MethodsForPost
from src.schemas.posts import PostCreate, PostDetail, PostOut, PostUpdate

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("/", response_model=PostOut, status_code=status.HTTP_201_CREATED)
def create_post(
    payload: PostCreate,
    author_nickname: str = Query(..., min_length=3),
    db: Session = Depends(get_db),
) -> PostOut:
    try:
        return MethodsForPost().create(db, payload, author_nickname)
    except PostDontCreateException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.get_detail())


@router.get("/", response_model=List[PostOut])
def list_posts(
    skip: int = 0,
    limit: int = 100,
    published_only: bool = True,
    db: Session = Depends(get_db),
) -> List[PostOut]:
    return MethodsForPost().get(db, skip, limit, published_only)


@router.get("/{post_id}", response_model=PostDetail)
def get_post(post_id: int, db: Session = Depends(get_db)) -> PostDetail:
    try:
        return MethodsForPost().get_detail(db, post_id)
    except PostNotFoundByIDException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.get_detail())


@router.put("/{post_id}", response_model=PostOut)
def update_post(
    post_id: int,
    payload: PostUpdate,
    author_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
) -> PostOut:
    try:
        return MethodsForPost().update(db, payload, post_id, author_id)
    except PostNotFoundByIDException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.get_detail())
    except PostDontChangeException as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.get_detail())


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    author_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
) -> None:
    try:
        MethodsForPost().destroy(db, post_id, author_id)
    except PostNotFoundByIDException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.get_detail())
    except PostDontDestroyException as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.get_detail())
