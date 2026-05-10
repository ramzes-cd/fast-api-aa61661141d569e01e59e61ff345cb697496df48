from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from src.core.exceptions.domain_exceptions import (
    CommentDontChangeException,
    CommentDontCreateException,
    CommentDontDestroyException,
    CommentNotFoundByIDException,
    PostNotFoundByIDException,
)
from src.domain.comments.use_cases.crud_comments import MethodsForComment
from src.schemas.comments import CommentCreate, CommentOut, CommentUpdate

router = APIRouter(prefix="/comments", tags=["comments"])


@router.get("/", response_model=list[CommentOut])
def list_comments(
    post_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> list[CommentOut]:
    try:
        return MethodsForComment().get(db, post_id, skip, limit)
    except PostNotFoundByIDException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.get_detail())


@router.get("/{comment_id}", response_model=CommentOut)
def get_comment(comment_id: int, db: Session = Depends(get_db)) -> CommentOut:
    try:
        return MethodsForComment().get_detail(db, comment_id)
    except CommentNotFoundByIDException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.get_detail())


@router.post("/", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
def create_comment(
    payload: CommentCreate,
    author_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
) -> CommentOut:
    try:
        return MethodsForComment().create(db, payload, author_id)
    except CommentDontCreateException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.get_detail())


@router.put("/{comment_id}", response_model=CommentOut)
def update_comment(
    comment_id: int,
    payload: CommentUpdate,
    author_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
) -> CommentOut:
    try:
        return MethodsForComment().update(db, comment_id, payload, author_id)
    except CommentNotFoundByIDException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.get_detail())
    except CommentDontChangeException as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.get_detail())


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: int,
    author_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
) -> None:
    try:
        MethodsForComment().destroy(db, comment_id, author_id)
    except CommentNotFoundByIDException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.get_detail())
    except CommentDontDestroyException as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.get_detail())
