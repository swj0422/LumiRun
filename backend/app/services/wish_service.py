from datetime import datetime
from typing import Optional, List
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.wish import Wish
from app.models.class_info import ClassInfo
from app.models.user import User
from app.core.logger import logger


class WishService:
    """学员心愿服务"""
    
    @staticmethod
    async def create_wish(
        db: AsyncSession,
        user_id: int,
        class_id: int,
        title: str,
        description: Optional[str] = None,
        image_urls: Optional[str] = None
    ) -> Wish:
        """创建学员心愿"""
        # 检查班级是否存在
        class_info = await db.execute(
            select(ClassInfo).where(ClassInfo.id == class_id)
        )
        class_info = class_info.scalar_one_or_none()
        
        if not class_info:
            raise ValueError("班级不存在")
        
        # 创建心愿
        wish = Wish(
            user_id=user_id,
            class_id=class_id,
            title=title,
            description=description,
            image_urls=image_urls,
            status=0,
            created_at=datetime.now()
        )
        
        db.add(wish)
        await db.commit()
        await db.refresh(wish)
        
        logger.info(f"学员 {user_id} 创建心愿: {title}, 班级ID {class_id}")
        return wish
    
    @staticmethod
    async def get_user_wishes(
        db: AsyncSession,
        user_id: int,
        status: Optional[int] = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[Wish], int]:
        """获取学员的心愿列表"""
        query = select(Wish).where(Wish.user_id == user_id)
        
        if status is not None:
            query = query.where(Wish.status == status)
        
        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar() or 0
        
        query = query.order_by(Wish.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        wishes = result.scalars().all()
        
        return wishes, total
    
    @staticmethod
    async def get_teacher_wishes(
        db: AsyncSession,
        teacher_id: int,
        class_id: Optional[int] = None,
        status: Optional[int] = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[Wish], int]:
        """获取导师班级的心愿列表"""
        classes = await db.execute(
            select(ClassInfo.id).where(ClassInfo.teacher_id == teacher_id)
        )
        class_ids = [c[0] for c in classes.all()]
        
        if not class_ids:
            return [], 0
        
        query = select(Wish).where(Wish.class_id.in_(class_ids))
        
        if class_id:
            query = query.where(Wish.class_id == class_id)
        if status is not None:
            query = query.where(Wish.status == status)
        
        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar() or 0
        
        query = query.order_by(Wish.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        wishes = result.scalars().all()
        
        return wishes, total