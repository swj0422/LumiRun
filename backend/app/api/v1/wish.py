from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.wish import Wish
from app.models.user import User
from app.services.wish_service import WishService
from pydantic import BaseModel, Field
import os
from datetime import datetime

router = APIRouter()


class WishCreate(BaseModel):
    content: str = Field(..., description="心愿内容（1-200字）")
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
    wish_data: WishCreate,
    image: UploadFile = File(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建心愿便利贴"""
    # 处理图片上传
    image_url = None
    if image:
        filename = f"wish_{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
        filepath = os.path.join("uploads", "wishes", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, "wb") as f:
            f.write(await image.read())
        
        image_url = f"/uploads/wishes/{filename}"
    
    wish = await WishService.create_wish(
        db=db,
        user_id=current_user.id,
        content=wish_data.content,
        image_url=image_url,
        is_anonymous=wish_data.is_anonymous
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
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取我的心愿便利贴列表"""
    wishes, total = await WishService.get_user_wishes(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    
    wish_list = []
    for wish in wishes:
        wish_list.append({
            "id": wish.id,
            "content": wish.content,
            "image_url": wish.image_url,
            "is_anonymous": wish.is_anonymous,
            "created_at": wish.created_at
        })
    
    return {
        "items": wish_list,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/")
async def get_public_wishes(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """获取公共心愿墙"""
    wishes, total = await WishService.get_public_wishes(
        db=db,
        skip=skip,
        limit=limit
    )
    
    wish_list = []
    for wish in wishes:
        # 获取用户名（如果不是匿名）
        user_name = None
        if not wish.is_anonymous:
            user = await db.execute(select(User).where(User.id == wish.user_id))
            user = user.scalar_one_or_none()
            user_name = user.real_name if user else None
        
        wish_list.append({
            "id": wish.id,
            "user_id": wish.user_id,
            "user_name": user_name,
            "content": wish.content,
            "image_url": wish.image_url,
            "is_anonymous": wish.is_anonymous,
            "created_at": wish.created_at
        })
    
    return {
        "items": wish_list,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.delete("/{wish_id}")
async def delete_wish(
    wish_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除心愿便利贴（软删除）"""
    success = await WishService.delete_wish(
        db=db,
        wish_id=wish_id,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="心愿不存在或无权删除"
        )
    
    return {
        "message": "删除成功"
    }
