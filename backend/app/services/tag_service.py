from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.tag import Tag, TagType
from app.core.logger import logger


class TagService:
    """标签服务类"""
    
    @staticmethod
    async def get_tags(db: AsyncSession, tag_type: Optional[TagType] = None) -> List[Tag]:
        """获取标签列表"""
        query = select(Tag)
        if tag_type:
            query = query.where(Tag.type == tag_type)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_tag_by_id(db: AsyncSession, tag_id: int) -> Optional[Tag]:
        """根据ID获取标签"""
        query = select(Tag).where(Tag.id == tag_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_tag(db: AsyncSession, name: str, tag_type: TagType, description: Optional[str] = None) -> Tag:
        """创建标签"""
        tag = Tag(
            name=name,
            type=tag_type,
            description=description
        )
        db.add(tag)
        await db.commit()
        await db.refresh(tag)
        return tag
    
    @staticmethod
    async def update_tag(db: AsyncSession, tag_id: int, name: Optional[str] = None, description: Optional[str] = None) -> Optional[Tag]:
        """更新标签"""
        tag = await TagService.get_tag_by_id(db, tag_id)
        if not tag:
            return None
        
        if name:
            tag.name = name
        if description is not None:
            tag.description = description
        
        await db.commit()
        await db.refresh(tag)
        return tag
    
    @staticmethod
    async def delete_tag(db: AsyncSession, tag_id: int) -> bool:
        """删除标签"""
        tag = await TagService.get_tag_by_id(db, tag_id)
        if not tag:
            return False
        
        await db.delete(tag)
        await db.commit()
        return True
