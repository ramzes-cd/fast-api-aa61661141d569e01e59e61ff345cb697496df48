from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

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
from src.schemas.users import UserOut
from src.services.auth import get_current_user

router = APIRouter(prefix="/comments", tags=["comments"], dependencies=[Depends(get_current_user)])


@router.get("/", response_model=list[CommentOut])
async def list_comments(
    post_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
) -> list[CommentOut]:
    try:
        return await MethodsForComment().get(db, post_id, skip, limit)
    except PostNotFoundByIDException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.get_detail()) from exc


@router.get("/{comment_id}", response_model=CommentOut)
async def get_comment(comment_id: int, db: AsyncSession = Depends(get_db)) -> CommentOut:
    try:
        return await MethodsForComment().get_detail(db, comment_id)
    except CommentNotFoundByIDException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.get_detail()) from exc


@router.post("/", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
async def create_comment(
    payload: CommentCreate,
    current_user: UserOut = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CommentOut:
    try:
        return await MethodsForComment().create(db, payload, current_user.id)
    except CommentDontCreateException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.get_detail()) from exc


@router.put("/{comment_id}", response_model=CommentOut)
async def update_comment(
    comment_id: int,
    payload: CommentUpdate,
    current_user: UserOut = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CommentOut:
    try:
        return await MethodsForComment().update(db, comment_id, payload, current_user.id)
    except CommentNotFoundByIDException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.get_detail()) from exc
    except CommentDontChangeException as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.get_detail()) from exc


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    current_user: UserOut = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    try:
        await MethodsForComment().destroy(db, comment_id, current_user.id)
    except CommentNotFoundByIDException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.get_detail()) from exc
    except CommentDontDestroyException as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.get_detail()) from exc
