from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from app.core.database import get_db
from app.core.security import get_current_user, require_teacher
from app.models.wish import Wish
from app.models.user import User
from app.models.class_info import ClassInfo
from app.models.class_student import ClassStudent
from app.services.wish_service import WishService
from pydantic import BaseModel, Field
import os
from datetime import datetime

router = APIRouter()


class WishCreate(BaseModel):
    title: str = Field(..., description="心愿标题")
    description: Optional[str] = Field(None, description="心愿描述")
    class_id: int = Field(..., description="班级ID")


class WishUpdate(BaseModel):
    title: Optional[str] = Field(None, description="心愿标题")
    description: Optional[str] = Field(None, description="心愿描述")


class WishProcess(BaseModel):
    status: int = Field(..., description="处理状态：1-已实现，2-已拒绝")
    teacher_comment: Optional[str] = Field(None, description="导师回复")


@router.post("/")
async def create_wish(
    wish_data: WishCreate,
    images: List[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """学员创建心愿"""
    # 验证班级是否属于该学员
    class_student = await db.execute(
        select(ClassStudent).where(
            ClassStudent.class_id == wish_data.class_id,
            ClassStudent.is_deleted == False
        ).join(
            ClassStudent.student_profile
        ).where(
            ClassStudent.student_profile.has(user_id=current_user.id)
        )
    )
    class_student = class_student.scalar_one_or_none()
    
    if not class_student:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权在该班级创建心愿"
        )
    
    # 处理图片上传（最多3张）
    image_urls = []
    if images:
        for i, image in enumerate(images[:3]):
            # 保存图片
            filename = f"wish_{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{i}.jpg"
            filepath = os.path.join("uploads", "wishes", filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, "wb") as f:
                f.write(await image.read())
            
            image_urls.append(f"/uploads/wishes/{filename}")
    
    wish = await WishService.create_wish(
        db=db,
        user_id=current_user.id,
        class_id=wish_data.class_id,
        title=wish_data.title,
        description=wish_data.description,
        image_urls=",".join(image_urls) if image_urls else None
    )
    
    return {
        "id": wish.id,
        "title": wish.title,
        "description": wish.description,
        "image_urls": wish.image_urls.split(",") if wish.image_urls else [],
        "class_id": wish.class_id,
        "status": wish.status,
        "status_text": "待处理",
        "created_at": wish.created_at
    }


@router.get("/my")
async def get_my_wishes(
    status: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取我的心愿列表（学员）"""
    wishes, total = await WishService.get_user_wishes(
        db=db,
        user_id=current_user.id,
        status=status,
        skip=skip,
        limit=limit
    )
    
    wish_list = []
    for wish in wishes:
        wish_list.append({
            "id": wish.id,
            "title": wish.title,
            "description": wish.description,
            "image_urls": wish.image_urls.split(",") if wish.image_urls else [],
            "class_id": wish.class_id,
            "status": wish.status,
            "status_text": ["待处理", "已实现", "已拒绝"][wish.status],
            "teacher_comment": wish.teacher_comment,
            "created_at": wish.created_at,
            "updated_at": wish.updated_at
        })
    
    return {
        "items": wish_list,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/teacher")
async def get_teacher_wishes(
    class_id: Optional[int] = Query(None),
    status: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    """获取导师班级的心愿列表"""
    wishes, total = await WishService.get_teacher_wishes(
        db=db,
        teacher_id=current_user.id,
        class_id=class_id,
        status=status,
        skip=skip,
        limit=limit
    )
    
    wish_list = []
    for wish in wishes:
        user = await db.execute(
            select(User).where(User.id == wish.user_id)
        )
        user = user.scalar_one_or_none()
        
        class_info = await db.execute(
            select(ClassInfo).where(ClassInfo.id == wish.class_id)
        )
        class_info = class_info.scalar_one_or_none()
        
        wish_list.append({
            "id": wish.id,
            "user_id": wish.user_id,
            "user_name": user.real_name if user else "",
            "class_id": wish.class_id,
            "class_name": f"{class_info.session or ''}级{class_info.class_name}班" if class_info else "",
            "title": wish.title,
            "description": wish.description,
            "image_urls": wish.image_urls.split(",") if wish.image_urls else [],
            "status": wish.status,
            "status_text": ["待处理", "已实现", "已拒绝"][wish.status],
            "teacher_comment": wish.teacher_comment,
            "created_at": wish.created_at,
            "updated_at": wish.updated_at
        })
    
    return {
        "items": wish_list,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.put("/{wish_id}")
async def update_wish(
    wish_id: int,
    wish_data: WishUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """学员更新心愿"""
    wish = await db.execute(
        select(Wish).where(Wish.id == wish_id, Wish.user_id == current_user.id)
    )
    wish = wish.scalar_one_or_none()
    
    if not wish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="心愿不存在或无权修改"
        )
    
    if wish.status != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="已处理的心愿不能修改"
        )
    
    if wish_data.title:
        wish.title = wish_data.title
    if wish_data.description:
        wish.description = wish_data.description
    
    await db.commit()
    
    return {
        "message": "更新成功"
    }


@router.delete("/{wish_id}")
async def delete_wish(
    wish_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """学员删除心愿"""
    wish = await db.execute(
        select(Wish).where(Wish.id == wish_id, Wish.user_id == current_user.id)
    )
    wish = wish.scalar_one_or_none()
    
    if not wish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="心愿不存在或无权删除"
        )
    
    if wish.status != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="已处理的心愿不能删除"
        )
    
    await db.delete(wish)
    await db.commit()
    
    return {
        "message": "删除成功"
    }


@router.post("/{wish_id}/process")
async def process_wish(
    wish_id: int,
    process_data: WishProcess,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    """导师处理心愿"""
    wish = await db.execute(select(Wish).where(Wish.id == wish_id))
    wish = wish.scalar_one_or_none()
    
    if not wish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="心愿不存在"
        )
    
    # 验证导师权限
    class_info = await db.execute(
        select(ClassInfo).where(ClassInfo.id == wish.class_id, ClassInfo.teacher_id == current_user.id)
    )
    class_info = class_info.scalar_one_or_none()
    
    if not class_info:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权处理该心愿"
        )
    
    wish.status = process_data.status
    wish.teacher_comment = process_data.teacher_comment
    
    await db.commit()
    
    return {
        "message": "处理成功",
        "status_text": ["待处理", "已实现", "已拒绝"][wish.status]
    }