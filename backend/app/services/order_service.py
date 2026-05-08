from datetime import datetime
from typing import Optional, List
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.gift_order import GiftOrder as Order
from app.models.gift import Gift

from app.models.user import User
from app.models.class_info import ClassInfo
from app.schemas.order import OrderCreate
from app.core.logger import logger
import qrcode
import base64
from io import BytesIO


class OrderService:
    """订单服务"""
    
    @staticmethod
    async def create_order(
        db: AsyncSession,
        order_data: OrderCreate,
        user_id: int
    ) -> Order:
        """创建兑换订单"""
        # 获取礼品信息
        gift = await db.execute(
            select(Gift).where(Gift.id == order_data.gift_id)
        )
        gift = gift.scalar_one_or_none()
        
        if not gift:
            raise ValueError("礼品不存在")
        
        if gift.status != 1:
            raise ValueError("礼品已下架")
        
        if gift.stock <= 0:
            raise ValueError("礼品库存不足")
        
        # 检查班级状态
        class_info = await db.execute(
            select(ClassInfo).where(ClassInfo.id == order_data.class_id)
        )
        class_info = class_info.scalar_one_or_none()
        
        if not class_info or not class_info.status:
            raise ValueError("班级不存在或已关闭")
        
        # 检查学员是否绑定班级
        from app.models.class_student import ClassStudent, BindStatus
        student_class = await db.execute(
            select(ClassStudent).where(
                ClassStudent.user_id == user_id,
                ClassStudent.class_id == order_data.class_id,
                ClassStudent.bind_status == BindStatus.APPROVED
            )
        )
        student_class = student_class.scalar_one_or_none()
        
        if not student_class:
            raise ValueError("您未绑定该班级")
        
        # 从GrowthLog表计算用户的成长值
        from app.models.growth_log import GrowthLog
        from app.models.class_student import ClassStudent
        
        # 获取用户在该班级的ClassStudent记录
        student_class = await db.execute(
            select(ClassStudent).where(
                ClassStudent.user_id == user_id,
                ClassStudent.class_id == order_data.class_id,
                ClassStudent.bind_status == BindStatus.APPROVED
            )
        )
        student_class = student_class.scalar_one_or_none()
        
        if not student_class:
            raise ValueError("您未绑定该班级")
        
        # 计算成长值
        growth_result = await db.execute(
            select(func.sum(GrowthLog.change_value)).where(
                GrowthLog.class_student_id == student_class.id
            )
        )
        available_score = growth_result.scalar() or 0
        
        if available_score < gift.price:
            raise ValueError("成长值不足")
        
        # 乐观锁处理库存
        gift.stock -= 1
        
        # 记录成长值扣减
        from app.models.user import User
        operator = await db.get(User, user_id)
        operator_name = operator.real_name if operator else "未知用户"
        
        # 记录成长值变动
        growth_log = GrowthLog(
            user_id=user_id,
            class_student_id=student_class.id,
            class_id=order_data.class_id,
            teacher_id=class_info.teacher_id,
            change_value=-gift.price,  # 负值表示扣减
            reason=f"兑换礼品：{gift.name}",
            operator_id=user_id,
            input_type=4,  # 系统调整，这样兑换记录不会被包括在总成长值中
            class_status=class_info.status
        )
        db.add(growth_log)
        
        # 创建订单
        order = Order(
            user_id=user_id,
            gift_id=gift.id,
            class_id=order_data.class_id,
            price=gift.price,
            status=1  # 待审核
        )
        
        # 生成兑换码（二维码）
        qr_code_data = f"order:{order.id}:{user_id}:{datetime.utcnow().timestamp()}"
        qr_code = qrcode.make(qr_code_data)
        
        # 转换为base64
        buffer = BytesIO()
        qr_code.save(buffer, format="PNG")
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        order.qr_code = qr_code_base64
        
        db.add(order)
        await db.commit()
        await db.refresh(order)
        
        logger.info(f"学员 {user_id} 兑换礼品: {gift.name}, 价格: {gift.price}")
        return order
    
    @staticmethod
    async def get_order_by_id(db: AsyncSession, order_id: int) -> Optional[Order]:
        """根据ID获取订单"""
        result = await db.execute(select(Order).where(Order.id == order_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_orders(
        db: AsyncSession,
        user_id: int,
        status: Optional[int] = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[Order], int]:
        """获取用户的订单"""
        base_query = select(Order).where(Order.user_id == user_id)
        
        if status is not None:
            base_query = base_query.where(Order.status == status)
        
        # 获取总数
        count_query = select(func.count()).select_from(base_query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        # 获取分页数据
        query = base_query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        orders = result.scalars().all()
        
        return orders, total
    
    @staticmethod
    async def get_teacher_orders(
        db: AsyncSession,
        teacher_id: int,
        class_id: Optional[int] = None,
        status: Optional[int] = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[Order], int]:
        """获取导师的订单"""
        # 获取导师的班级
        classes = await db.execute(
            select(ClassInfo.id).where(ClassInfo.teacher_id == teacher_id)
        )
        class_ids = [c[0] for c in classes.all()]
        
        if not class_ids:
            return [], 0
        
        base_query = select(Order).where(Order.class_id.in_(class_ids))
        
        if class_id:
            base_query = base_query.where(Order.class_id == class_id)
        
        if status is not None:
            base_query = base_query.where(Order.status == status)
        
        # 获取总数
        count_query = select(func.count()).select_from(base_query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        # 获取分页数据
        query = base_query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        orders = result.scalars().all()
        
        return orders, total
    
    @staticmethod
    async def approve_order(
        db: AsyncSession,
        order_id: int,
        teacher_id: int
    ) -> Order:
        """审核通过订单"""
        order = await OrderService.get_order_by_id(db, order_id)
        if not order:
            raise ValueError("订单不存在")
        
        # 检查权限
        class_info = await db.execute(
            select(ClassInfo).where(ClassInfo.id == order.class_id)
        )
        class_info = class_info.scalar_one_or_none()
        
        if not class_info or class_info.teacher_id != teacher_id:
            raise ValueError("无权限操作此订单")
        
        if order.status != 1:
            raise ValueError("订单状态错误")
        
        order.status = 2  # 已审核
        order.approved_at = datetime.utcnow()
        order.approved_by = teacher_id
        
        await db.commit()
        await db.refresh(order)
        
        logger.info(f"导师 {teacher_id} 审核通过订单: {order.id}")
        return order
    
    @staticmethod
    async def reject_order(
        db: AsyncSession,
        order_id: int,
        teacher_id: int,
        reason: str
    ) -> Order:
        """拒绝订单"""
        order = await OrderService.get_order_by_id(db, order_id)
        if not order:
            raise ValueError("订单不存在")
        
        # 检查权限
        class_info = await db.execute(
            select(ClassInfo).where(ClassInfo.id == order.class_id)
        )
        class_info = class_info.scalar_one_or_none()
        
        if not class_info or class_info.teacher_id != teacher_id:
            raise ValueError("无权限操作此订单")
        
        if order.status != 1:
            raise ValueError("订单状态错误")
        
        # 恢复库存
        gift = await db.execute(
            select(Gift).where(Gift.id == order.gift_id)
        )
        gift = gift.scalar_one_or_none()
        if gift:
            gift.stock += 1
        
        # 恢复成长值
        from app.models.growth_log import GrowthLog
        from app.models.class_student import ClassStudent
        
        # 获取用户在该班级的ClassStudent记录
        student_class = await db.execute(
            select(ClassStudent).where(
                ClassStudent.user_id == order.user_id,
                ClassStudent.class_id == order.class_id,
                ClassStudent.bind_status == BindStatus.APPROVED
            )
        )
        student_class = student_class.scalar_one_or_none()
        
        if student_class:
            # 记录成长值恢复
            growth_log = GrowthLog(
                user_id=order.user_id,
                class_student_id=student_class.id,
                class_id=order.class_id,
                teacher_id=class_info.teacher_id,
                change_value=order.price,  # 正值表示恢复
                reason=f"拒绝兑换礼品：{gift.name}，原因：{reason}",
                operator_id=teacher_id,
                input_type=4,  # 系统调整，这样恢复成长值的记录不会被包括在总成长值中
                class_status=class_info.status
            )
            db.add(growth_log)
        
        # 更新订单状态
        order.status = 3  # 已拒绝
        order.rejected_at = datetime.utcnow()
        order.rejected_by = teacher_id
        order.reject_reason = reason
        
        await db.commit()
        await db.refresh(order)
        
        logger.info(f"导师 {teacher_id} 拒绝订单: {order.id}, 原因: {reason}")
        return order
