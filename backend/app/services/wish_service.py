from datetime import datetime
from typing import Optional, List
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.wish import Wish
from app.models.gift import Gift
from app.models.class_info import ClassInfo
from app.models.user import User
from app.core.logger import logger


class WishService:
    """学员心愿服务"""
    
    @staticmethod
    async def create_wish(
        db: AsyncSession,
        user_id: int,
        gift_id: int,
        class_id: int
    ) -> Wish:
        """创建学员心愿"""
        # 检查礼品是否存在
        gift = await db.execute(
            select(Gift).where(Gift.id == gift_id)
        )
        gift = gift.scalar_one_or_none()
        
        if not gift:
            raise ValueError("礼品不存在")
        
        # 检查班级是否存在
        class_info = await db.execute(
            select(ClassInfo).where(ClassInfo.id == class_id)
        )
        class_info = class_info.scalar_one_or_none()
        
        if not class_info:
            raise ValueError("班级不存在")
        
        # 检查学员是否绑定了该班级
        from app.models.class_student import ClassStudent, BindStatus
        student_class = await db.execute(
            select(ClassStudent).where(
                ClassStudent.user_id == user_id,
                ClassStudent.class_id == class_id,
                ClassStudent.bind_status == BindStatus.APPROVED
            )
        )
        student_class = student_class.scalar_one_or_none()
        
        if not student_class:
            raise ValueError("您未绑定该班级")
        
        # 检查是否已存在相同的心愿
        existing = await db.execute(
            select(Wish).where(
                Wish.user_id == user_id,
                Wish.gift_id == gift_id,
                Wish.class_id == class_id,
                Wish.status == True
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("您已经添加过此心愿")
        
        # 创建心愿
        wish = Wish(
            user_id=user_id,
            gift_id=gift_id,
            class_id=class_id,
            status=True,
            created_at=datetime.utcnow()
        )
        
        db.add(wish)
        await db.commit()
        await db.refresh(wish)
        
        logger.info(f"学员 {user_id} 添加心愿: 礼品ID {gift_id}, 班级ID {class_id}")
        return wish
    
    @staticmethod
    async def get_user_wishes(
        db: AsyncSession,
        user_id: int,
        status: Optional[bool] = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[Wish], int]:
        """获取学员的心愿列表"""
        # 构建查询条件
        query = select(Wish).where(Wish.user_id == user_id)
        
        if status is not None:
            query = query.where(Wish.status == status)
        
        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar()
        
        # 获取分页数据
        query = query.order_by(Wish.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        wishes = result.scalars().all()
        
        return wishes, total
    
    @staticmethod
    async def get_class_wishes(
        db: AsyncSession,
        teacher_id: int,
        class_id: Optional[int] = None,
        status: Optional[bool] = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[Wish], int]:
        """获取导师班级的心愿列表"""
        # 获取导师的班级
        classes = await db.execute(
            select(ClassInfo.id).where(ClassInfo.teacher_id == teacher_id)
        )
        class_ids = [c[0] for c in classes.all()]
        
        if not class_ids:
            return [], 0
        
        # 构建查询条件
        query = select(Wish).where(Wish.class_id.in_(class_ids))
        
        if class_id:
            query = query.where(Wish.class_id == class_id)
        if status is not None:
            query = query.where(Wish.status == status)
        
        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar()
        
        # 获取分页数据
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
        """删除学员心愿"""
        result = await db.execute(
            Wish.__table__.delete().where(
                Wish.id == wish_id,
                Wish.user_id == user_id
            )
        )
        
        await db.commit()
        
        if result.rowcount > 0:
            logger.info(f"删除心愿: 心愿ID {wish_id}, 用户ID {user_id}")
            return True
        else:
            return False
    
    @staticmethod
    async def process_wishes(
        db: AsyncSession
    ) -> int:
        """处理心愿（库存通知）"""
        # 查找未处理的心愿
        result = await db.execute(
            select(Wish).where(Wish.status == True)
        )
        wishes = result.scalars().all()
        
        processed_count = 0
        for wish in wishes:
            # 检查礼品库存
            from app.models.gift_stock import GiftStock
            gift_stock = await db.execute(
                select(GiftStock).where(GiftStock.gift_id == wish.gift_id)
            )
            gift_stock = gift_stock.scalar_one_or_none()
            
            # 检查礼品状态
            gift = await db.execute(
                select(Gift).where(Gift.id == wish.gift_id)
            )
            gift = gift.scalar_one_or_none()
            
            if gift and gift_stock and gift_stock.current_stock > 0 and gift.status:
                # 更新心愿状态
                wish.status = False
                wish.notified_at = datetime.utcnow()
                
                # 发送通知
                from app.services.message_service import MessageService
                await MessageService.create_message(
                    db=db,
                    user_id=wish.user_id,
                    content=f"您心愿中的【{gift.name}】已补货，快来兑换吧！",
                    message_type=2
                )
                
                processed_count += 1
        
        if processed_count > 0:
            await db.commit()
        
        logger.info(f"处理心愿: 处理了 {processed_count} 个心愿")
        return processed_count
