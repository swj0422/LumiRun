from datetime import datetime
from typing import Optional, List
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.wish import Wish
from app.models.class_info import ClassInfo
from app.models.user import User
from app.core.logger import logger


class WishService:
    """心愿便利贴服务"""
    
    @staticmethod
    async def create_wish(
        db: AsyncSession,
        user_id: int,
        content: str,
        class_student_id: Optional[int] = None,
        image_url: Optional[str] = None,
        is_anonymous: int = 0
    ) -> Wish:
        """创建心愿便利贴"""
        if not content or len(content) > 200:
            raise ValueError("心愿内容必须在1-200字之间")
        
        wish = Wish(
            user_id=user_id,
            class_student_id=class_student_id,
            content=content,
            image_url=image_url,
            is_anonymous=is_anonymous,
            is_deleted=0,
            created_at=datetime.now()
        )
        
        db.add(wish)
        await db.commit()
        await db.refresh(wish)
        
        logger.info(f"用户 {user_id} 创建心愿便利贴")
        return wish
    
    @staticmethod
    async def get_user_wishes(
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[Wish], int]:
        """获取用户的心愿便利贴列表"""
        query = select(Wish).where(Wish.user_id == user_id, Wish.is_deleted == 0)
        
        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar() or 0
        
        query = query.order_by(Wish.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        wishes = result.scalars().all()
        
        return wishes, total
    
    @staticmethod
    async def get_public_wishes(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[Wish], int]:
        """获取公共心愿墙（匿名和非匿名）"""
        query = select(Wish).where(Wish.is_deleted == 0)
        
        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar() or 0
        
        query = query.order_by(Wish.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        wishes = result.scalars().all()
        
        return wishes, total
    
    @staticmethod
    async def delete_wish(
        db: AsyncSession,
        wish_id: int,
        user_id: int
    ) -> bool:
        """软删除心愿便利贴"""
        wish = await db.execute(
            select(Wish).where(Wish.id == wish_id, Wish.user_id == user_id)
        )
        wish = wish.scalar_one_or_none()
        
        if not wish:
            return False
        
        wish.is_deleted = 1
        await db.commit()
        
        logger.info(f"用户 {user_id} 删除心愿便利贴: {wish_id}")
        return True
