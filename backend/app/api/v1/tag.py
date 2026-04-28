from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.tag import Tag, TagType
from app.services.tag_service import TagService

router = APIRouter()


class TagCreate(BaseModel):
    name: str
    type: TagType
    description: Optional[str] = None


class TagUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


@router.get("/", response_model=dict)
async def get_tags(
    type: Optional[TagType] = Query(None, description="标签类型"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取标签列表"""
    tags = await TagService.get_tags(db, type)
    tag_list = [
        {
            "id": tag.id,
            "name": tag.name,
            "type": tag.type,
            "description": tag.description,
            "created_at": tag.created_at,
            "updated_at": tag.updated_at
        }
        for tag in tags
    ]
    return {
        "items": tag_list,
        "total": len(tag_list)
    }


@router.get("/{tag_id}", response_model=dict)
async def get_tag(
    tag_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取标签详情"""
    tag = await TagService.get_tag_by_id(db, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    return {
        "id": tag.id,
        "name": tag.name,
        "type": tag.type,
        "description": tag.description,
        "created_at": tag.created_at,
        "updated_at": tag.updated_at
    }


@router.post("/", response_model=dict)
async def create_tag(
    tag_data: TagCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建标签"""
    tag = await TagService.create_tag(db, tag_data.name, tag_data.type, tag_data.description)
    return {
        "id": tag.id,
        "name": tag.name,
        "type": tag.type,
        "description": tag.description,
        "created_at": tag.created_at,
        "updated_at": tag.updated_at
    }


@router.put("/{tag_id}", response_model=dict)
async def update_tag(
    tag_id: int,
    tag_data: TagUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新标签"""
    tag = await TagService.update_tag(db, tag_id, tag_data.name, tag_data.description)
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    return {
        "id": tag.id,
        "name": tag.name,
        "type": tag.type,
        "description": tag.description,
        "created_at": tag.created_at,
        "updated_at": tag.updated_at
    }


@router.delete("/{tag_id}", response_model=dict)
async def delete_tag(
    tag_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除标签"""
    success = await TagService.delete_tag(db, tag_id)
    if not success:
        raise HTTPException(status_code=404, detail="标签不存在")
    return {"message": "标签删除成功"}
