from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.core.config import get_settings
from app.models.wish import Wish
from app.models.user import User
from app.services.wish_service import WishService
from pydantic import BaseModel, Field
import os
from datetime import datetime

router = APIRouter()


class WishCreate(BaseModel):
    title: str = Field(..., description="心愿标题（1-50字）")
    description: Optional[str] = Field(None, description="心愿描述（可选）")
    class_id: Optional[int] = Field(None, description="组织ID（可选）")
    is_anonymous: Optional[int] = Field(0, description="是否匿名：0-不匿名，1-匿名")


class WishResponse(BaseModel):
    id: int
    user_id: int
    user_name: Optional[str]
    content: str
    image_url: Optional[str]
    is_anonymous: int
    created_at: datetime


@router.post("/", response_model=WishResponse)
async def create_wish(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    class_id: Optional[str] = Form(None),
    is_anonymous: Optional[str] = Form("0"),
    images: List[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建心愿便利贴"""
    # 处理图片上传（取第一张）
    image_url = None
    if images and len(images) > 0:
        image = images[0]
        if image and image.filename:
            filename = f"wish_{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
            upload_dir = os.path.join(get_settings().UPLOAD_DIR, "wishes")
            os.makedirs(upload_dir, exist_ok=True)
            filepath = os.path.join(upload_dir, filename)

            with open(filepath, "wb") as f:
                f.write(await image.read())

            image_url = f"/uploads/wishes/{filename}"

    # 处理 is_anonymous
    is_anon = 0
    if is_anonymous and is_anonymous not in ["0", "false", ""]:
        is_anon = 1

    # 使用 title 作为 content
    content = title
    if description:
        content = f"{title}\n{description}"

    wish = await WishService.create_wish(
        db=db,
        user_id=current_user.id,
        content=content,
        image_url=image_url,
        is_anonymous=is_anon
    )

    return WishResponse(
        id=wish.id,
        user_id=wish.user_id,
        user_name=None if wish.is_anonymous else current_user.real_name,
        content=wish.content,
        image_url=wish.image_url,
        is_anonymous=wish.is_anonymous,
        created_at=wish.created_at
    )


@router.get("/my")
async def get_my_wishes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """获取我的心愿列表"""
    wishes, total = await WishService.get_user_wishes(
        db=db,
        user_id=current_user.id,
        page=page,
        page_size=page_size
    )

    return {
        "items": [
            WishResponse(
                id=w.id,
                user_id=w.user_id,
                user_name=None if w.is_anonymous else current_user.real_name,
                content=w.content,
                image_url=w.image_url,
                is_anonymous=w.is_anonymous,
                created_at=w.created_at
            ) for w in wishes
        ],
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/public")
async def get_public_wishes(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """获取公开心愿列表"""
    wishes, total = await WishService.get_public_wishes(
        db=db,
        page=page,
        page_size=page_size
    )

    return {
        "items": [
            WishResponse(
                id=w.id,
                user_id=w.user_id,
                user_name=None if w.is_anonymous else w.user.real_name if w.user else None,
                content=w.content,
                image_url=w.image_url,
                is_anonymous=w.is_anonymous,
                created_at=w.created_at
            ) for w in wishes
        ],
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.put("/{wish_id}", response_model=WishResponse)
async def update_wish(
    wish_id: int,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    is_anonymous: Optional[str] = Form("0"),
    images: List[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新心愿"""
    # 获取心愿
    result = await db.execute(select(Wish).where(Wish.id == wish_id))
    wish = result.scalar_one_or_none()

    if not wish:
        raise HTTPException(status_code=404, detail="心愿不存在")

    # 检查权限
    if wish.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限修改此心愿")

    # 处理图片上传（取第一张）
    image_url = wish.image_url
    if images and len(images) > 0:
        image = images[0]
        if image and image.filename:
            filename = f"wish_{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
            upload_dir = os.path.join(get_settings().UPLOAD_DIR, "wishes")
            os.makedirs(upload_dir, exist_ok=True)
            filepath = os.path.join(upload_dir, filename)

            with open(filepath, "wb") as f:
                f.write(await image.read())

            image_url = f"/uploads/wishes/{filename}"

    # 处理 is_anonymous
    is_anon = 0
    if is_anonymous and is_anonymous not in ["0", "false", ""]:
        is_anon = 1

    # 更新内容
    content = title
    if description:
        content = f"{title}\n{description}"
    elif wish.content:
        content = wish.content

    updated_wish = await WishService.update_wish(
        db=db,
        wish_id=wish_id,
        content=content,
        image_url=image_url,
        is_anonymous=is_anon
    )

    return WishResponse(
        id=updated_wish.id,
        user_id=updated_wish.user_id,
        user_name=None if updated_wish.is_anonymous else current_user.real_name,
        content=updated_wish.content,
        image_url=updated_wish.image_url,
        is_anonymous=updated_wish.is_anonymous,
        created_at=updated_wish.created_at
    )


@router.delete("/{wish_id}")
async def delete_wish(
    wish_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除心愿"""
    # 获取心愿
    result = await db.execute(select(Wish).where(Wish.id == wish_id))
    wish = result.scalar_one_or_none()

    if not wish:
        raise HTTPException(status_code=404, detail="心愿不存在")

    # 检查权限（自己的或者管理员）
    if wish.user_id != current_user.id and current_user.role_id not in [1, 2]:
        raise HTTPException(status_code=403, detail="无权限删除此心愿")

    await WishService.delete_wish(db=db, wish_id=wish_id)

    return {"message": "删除成功"}


@router.delete("/admin/{wish_id}")
async def admin_delete_wish(
    wish_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """管理员删除任意心愿"""
    # 获取心愿
    result = await db.execute(select(Wish).where(Wish.id == wish_id))
    wish = result.scalar_one_or_none()

    if not wish:
        raise HTTPException(status_code=404, detail="心愿不存在")

    await WishService.delete_wish(db=db, wish_id=wish_id)

    return {"message": "删除成功"}
