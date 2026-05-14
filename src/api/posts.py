from datetime import datetime
import mimetypes
from pathlib import Path
from typing import List
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from src.core.exceptions.domain_exceptions import (
    PostDontChangeException,
    PostDontCreateException,
    PostDontDestroyException,
    PostNotFoundByIDException,
)
from src.domain.posts.use_cases.crud_posts import MethodsForPost
from src.schemas.posts import PostCreate, PostDetail, PostOut, PostUpdate
from src.schemas.users import UserOut
from src.services.auth import get_current_user

router = APIRouter(prefix="/posts", tags=["posts"], dependencies=[Depends(get_current_user)])
UPLOAD_DIR = Path("uploads/posts")
ALLOWED_IMAGE_TYPES = {"image/png": ".png", "image/jpeg": ".jpg"}


@router.post("/", response_model=PostOut, status_code=status.HTTP_201_CREATED)
async def create_post(
    title: str = Form(...),
    text: str = Form(...),
    pub_date: datetime = Form(...),
    location_name: str = Form(...),
    category_slug: str = Form(...),
    is_published: bool = Form(True),
    image_file: UploadFile | None = File(default=None),
    current_user: UserOut = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PostOut:
    image_path: str | None = None
    if image_file is not None and image_file.filename:
        extension = ALLOWED_IMAGE_TYPES.get(image_file.content_type or "")
        if extension is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Поддерживаются только изображения PNG и JPG.",
            )

        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        image_name = f"{uuid4().hex}{extension}"
        destination = UPLOAD_DIR / image_name
        body = await image_file.read()
        destination.write_bytes(body)
        image_path = f"/media/posts/{image_name}"

    try:
        payload = PostCreate(
            title=title,
            text=text,
            pub_date=pub_date,
            location_name=location_name,
            category_slug=category_slug,
            is_published=is_published,
            image=image_path,
        )
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=exc.errors(),
        ) from exc

    try:
        return await MethodsForPost().create(db, payload, current_user.nickname)
    except PostDontCreateException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.get_detail()) from exc


@router.get("/", response_model=List[PostOut])
async def list_posts(
    skip: int = 0,
    limit: int = 100,
    published_only: bool = True,
    db: AsyncSession = Depends(get_db),
) -> List[PostOut]:
    return await MethodsForPost().get(db, skip, limit, published_only)


@router.get("/{post_id}", response_model=PostDetail)
async def get_post(post_id: int, db: AsyncSession = Depends(get_db)) -> PostDetail:
    try:
        return await MethodsForPost().get_detail(db, post_id)
    except PostNotFoundByIDException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.get_detail()) from exc


@router.get("/{post_id}/image", response_class=FileResponse)
async def get_post_image(post_id: int, db: AsyncSession = Depends(get_db)) -> FileResponse:
    try:
        post = await MethodsForPost().get_detail(db, post_id)
    except PostNotFoundByIDException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.get_detail()) from exc

    if not post.image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="У поста нет изображения.")

    image_path = Path(str(post.image).replace("/media/", "uploads/").lstrip("/"))
    if not image_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Файл изображения не найден.")

    media_type, _ = mimetypes.guess_type(str(image_path))
    return FileResponse(path=image_path, media_type=media_type or "application/octet-stream")


@router.put("/{post_id}", response_model=PostOut)
async def update_post(
    post_id: int,
    payload: PostUpdate,
    current_user: UserOut = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PostOut:
    try:
        return await MethodsForPost().update(db, payload, post_id, current_user.id)
    except PostNotFoundByIDException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.get_detail()) from exc
    except PostDontChangeException as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.get_detail()) from exc


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    current_user: UserOut = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    try:
        await MethodsForPost().destroy(db, post_id, current_user.id)
    except PostNotFoundByIDException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.get_detail()) from exc
    except PostDontDestroyException as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.get_detail()) from exc
