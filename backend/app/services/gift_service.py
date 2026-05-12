from datetime import datetime
from typing import Optional, List
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.gift import Gift
from app.models.gift_class_relation import GiftClassRelation as GiftClass
from app.models.class_info import ClassInfo
from app.schemas.gift import GiftCreate, GiftUpdate, GiftClassCreate
from app.core.logger import logger
import os
from app.core.config import get_settings


class GiftService:
    """礼品服务"""
    
    @staticmethod
    async def get_gift_by_id(db: AsyncSession, gift_id: int) -> Optional[Gift]:
        """根据ID获取礼品"""
        result = await db.execute(select(Gift).where(Gift.id == gift_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_gifts(
        db: AsyncSession,
        teacher_id: int,
        status: Optional[int] = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[Gift], int]:
        """获取礼品列表"""
        # 获取导师的班级
        classes = await db.execute(
            select(ClassInfo.id).where(ClassInfo.teacher_id == teacher_id)
        )
        class_ids = [c[0] for c in classes.all()]
        
        if not class_ids:
            return [], 0
        
        # 构建基础查询条件
        base_query = select(Gift)
        if status is not None:
            base_query = base_query.where(Gift.status == status)
        
        # 获取总数
        count_query = select(func.count()).select_from(base_query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        # 获取分页数据
        query = base_query.order_by(Gift.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        gifts = result.scalars().all()
        
        return gifts, total
    
    @staticmethod
    async def create_gift(
        db: AsyncSession,
        gift_data: GiftCreate,
        teacher_id: int,
        image_path: Optional[str] = None
    ) -> Gift:
        """创建礼品"""
        gift = Gift(
            name=gift_data.name,
            description=gift_data.description,
            price=gift_data.price,
            stock=gift_data.stock,
            status=1,  # 默认上架
            image_path=image_path,
            created_by=teacher_id
        )
        
        db.add(gift)
        await db.commit()
        await db.refresh(gift)
        
        logger.info(f"创建礼品: {gift.name}, 价格: {gift.price}, 库存: {gift.stock}")
        return gift
    
    @staticmethod
    async def update_gift(
        db: AsyncSession,
        gift_id: int,
        gift_data: GiftUpdate,
        teacher_id: int,
        image_path: Optional[str] = None
    ) -> Gift:
        """更新礼品"""
        gift = await GiftService.get_gift_by_id(db, gift_id)
        if not gift:
            raise ValueError("礼品不存在")
        
        # 检查是否有兑换记录
        from app.models.order import Order
        orders = await db.execute(
            select(Order).where(Order.gift_id == gift_id)
        )
        has_orders = orders.scalar_one_or_none() is not None
        
        # 检查是否有心愿记录
        from app.models.wish import Wish
        wishes = await db.execute(
            select(Wish).where(Wish.gift_id == gift_id)
        )
        has_wishes = wishes.scalar_one_or_none() is not None
        
        if has_orders or has_wishes:
            # 提示用户
            logger.warning(f"礼品 {gift.name} 有兑换记录或心愿，修改需谨慎")
        
        # 更新字段
        if gift_data.name is not None:
            gift.name = gift_data.name
        if gift_data.description is not None:
            gift.description = gift_data.description
        if gift_data.price is not None:
            gift.price = gift_data.price
        if gift_data.stock is not None:
            gift.stock = gift_data.stock
        if gift_data.status is not None:
            gift.status = gift_data.status
        if image_path:
            gift.image_path = image_path
        
        gift.updated_by = teacher_id
        gift.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(gift)
        
        logger.info(f"更新礼品: {gift.name}")
        return gift
    
    @staticmethod
    async def delete_gift(db: AsyncSession, gift_id: int, teacher_id: int) -> bool:
        """删除礼品"""
        gift = await GiftService.get_gift_by_id(db, gift_id)
        if not gift:
            raise ValueError("礼品不存在")
        
        # 检查是否有兑换记录
        from app.models.order import Order
        orders = await db.execute(
            select(Order).where(Order.gift_id == gift_id)
        )
        if orders.scalar_one_or_none():
            raise ValueError("礼品已被兑换，无法删除")
        
        # 检查是否有心愿记录
        from app.models.wish import Wish
        wishes = await db.execute(
            select(Wish).where(Wish.gift_id == gift_id)
        )
        if wishes.scalar_one_or_none():
            raise ValueError("礼品有心愿记录，无法删除")
        
        # 删除礼品-班级关联
        await db.execute(
            GiftClass.__table__.delete().where(GiftClass.gift_id == gift_id)
        )
        
        # 删除礼品
        await db.delete(gift)
        await db.commit()
        
        # 删除图片文件（Windows兼容）
        if gift.image_path:
            try:
                settings = get_settings()
                image_full_path = settings.UPLOAD_DIR / gift.image_path
                if image_full_path.exists():
                    image_full_path.unlink()
            except Exception as e:
                logger.error(f"删除礼品图片失败: {e}")
        
        logger.info(f"删除礼品: {gift.name}")
        return True
    
    @staticmethod
    async def add_gift_class(
        db: AsyncSession,
        gift_class_data: GiftClassCreate,
        teacher_id: int
    ) -> GiftClass:
        """添加礼品开放班级"""
        # 检查礼品是否存在
        gift = await GiftService.get_gift_by_id(db, gift_class_data.gift_id)
        if not gift:
            raise ValueError("礼品不存在")
        
        # 检查班级是否存在且属于当前导师
        class_info = await db.execute(
            select(ClassInfo).where(
                ClassInfo.id == gift_class_data.class_id,
                ClassInfo.teacher_id == teacher_id
            )
        )
        class_info = class_info.scalar_one_or_none()
        
        if not class_info:
            raise ValueError("班级不存在或不属于当前导师")
        
        # 检查是否已存在关联
        existing = await db.execute(
            select(GiftClass).where(
                GiftClass.gift_id == gift_class_data.gift_id,
                GiftClass.class_id == gift_class_data.class_id
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("礼品已开放给该班级")
        
        gift_class = GiftClass(
            gift_id=gift_class_data.gift_id,
            class_id=gift_class_data.class_id
        )
        
        db.add(gift_class)
        await db.commit()
        await db.refresh(gift_class)
        
        logger.info(f"礼品 {gift.name} 开放给班级 {class_info.class_name}")
        return gift_class
    
    @staticmethod
    async def remove_gift_class(
        db: AsyncSession,
        gift_id: int,
        class_id: int,
        teacher_id: int
    ) -> bool:
        """移除礼品开放班级"""
        # 检查礼品是否存在
        gift = await GiftService.get_gift_by_id(db, gift_id)
        if not gift:
            raise ValueError("礼品不存在")
        
        # 检查班级是否存在且属于当前导师
        class_info = await db.execute(
            select(ClassInfo).where(
                ClassInfo.id == class_id,
                ClassInfo.teacher_id == teacher_id
            )
        )
        class_info = class_info.scalar_one_or_none()
        
        if not class_info:
            raise ValueError("班级不存在或不属于当前导师")
        
        # 检查是否有兑换记录
        from app.models.order import Order
        orders = await db.execute(
            select(Order).where(
                Order.gift_id == gift_id,
                Order.class_id == class_id
            )
        )
        if orders.scalar_one_or_none():
            raise ValueError("该班级有兑换记录，无法移除")
        
        # 检查是否有心愿记录
        from app.models.wish import Wish
        wishes = await db.execute(
            select(Wish).where(
                Wish.gift_id == gift_id,
                Wish.class_id == class_id
            )
        )
        if wishes.scalar_one_or_none():
            raise ValueError("该班级有心愿记录，无法移除")
        
        # 删除关联
        result = await db.execute(
            GiftClass.__table__.delete().where(
                GiftClass.gift_id == gift_id,
                GiftClass.class_id == class_id
            )
        )
        
        await db.commit()
        
        if result.rowcount > 0:
            logger.info(f"移除礼品 {gift.name} 对班级 {class_info.class_name} 的开放")
            return True
        else:
            raise ValueError("关联不存在")
    
    @staticmethod
    async def get_gift_classes(db: AsyncSession, gift_id: int) -> List[dict]:
        """获取礼品开放的班级"""
        result = await db.execute(
            select(
                GiftClass.class_id,
                ClassInfo.class_name,
                ClassInfo.school_name
            ).join(
                ClassInfo, ClassInfo.id == GiftClass.class_id
            ).where(
                GiftClass.gift_id == gift_id
            )
        )
        
        classes = []
        for row in result.all():
            classes.append({
                "class_id": row[0],
                "class_name": row[1],
                "school_name": row[2]
            })
        
        return classes
    
    @staticmethod
    async def get_available_gifts(
        db: AsyncSession,
        student_id: int
    ) -> List[dict]:
        """获取学员可兑换的礼品"""
        # 获取学员绑定的班级
        from app.models.class_student import ClassStudent
        student_classes = await db.execute(
            select(ClassStudent.class_id).where(
                ClassStudent.user_id == student_id,
                ClassStudent.status == 1
            )
        )
        class_ids = [sc[0] for sc in student_classes.all()]
        
        if not class_ids:
            return []
        
        # 查询可兑换的礼品
        result = await db.execute(
            select(
                Gift.id,
                Gift.name,
                Gift.description,
                Gift.price,
                Gift.stock,
                Gift.image_path
            ).join(
                GiftClass, GiftClass.gift_id == Gift.id
            ).where(
                GiftClass.class_id.in_(class_ids),
                Gift.status == 1,  # 上架状态
                Gift.stock > 0      # 有库存
            ).distinct()
        )
        
        gifts = []
        for row in result.all():
            gifts.append({
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "price": row[3],
                "stock": row[4],
                "image_path": row[5]
            })
        
        return gifts

# 导入ClassStudent
from app.models.class_student import ClassStudent
