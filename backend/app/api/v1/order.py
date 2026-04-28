from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import Optional, List
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_user, require_teacher
from app.models.gift_order import GiftOrder
from app.models.gift import Gift
from app.models.gift_stock import GiftStock
from app.models.class_info import ClassInfo
from app.models.user import User

from pydantic import BaseModel, Field
from app.core.logger import logger

router = APIRouter()


class OrderReject(BaseModel):
    reason: str = Field(..., description="拒绝原因")


class VerifyOrder(BaseModel):
    qr_code: str = Field(..., description="核销码")


class OrderCreate(BaseModel):
    gift_id: int
    class_id: int
    quantity: int = Field(default=1, description="兑换数量")


@router.get("/")
async def get_orders(
    class_id: Optional[int] = Query(None),
    status: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    """获取导师的订单列表"""
    try:
        # 超级管理员和管理员可以查看所有订单
        if current_user.role and current_user.role.role_name in ["super_admin", "admin"]:
            query = select(GiftOrder)
        else:
            query = select(GiftOrder).where(GiftOrder.teacher_id == current_user.id)
        
        # 只返回待处理的订单（状态为0待审核或1待核销）
        from sqlalchemy import or_
        query = query.where(or_(GiftOrder.status == 0, GiftOrder.status == 1))
        
        if class_id:
            query = query.where(GiftOrder.class_id == class_id)
        if status:
            query = query.where(GiftOrder.status == status)
        
        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar() or 0
        
        query = query.order_by(GiftOrder.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        orders = result.scalars().all()
        
        order_list = []
        for order in orders:
            try:
                # 查询ClassStudent信息，预加载student_profile关系
                from app.models.class_student import ClassStudent
                from app.models.student_profile import StudentProfile
                from sqlalchemy.orm import selectinload
                student_result = await db.execute(
                    select(ClassStudent).options(
                        selectinload(ClassStudent.student_profile).selectinload(StudentProfile.user)
                    ).where(ClassStudent.id == order.class_student_id)
                )
                student = student_result.scalar_one_or_none()
                
                # 获取学生姓名
                student_name = ""
                if student:
                    try:
                        if student.student_profile and student.student_profile.user:
                            student_name = student.student_profile.user.real_name
                        else:
                            student_name = student.name_in_class or ""
                    except Exception as e:
                        student_name = student.name_in_class if student else ""
                        logger.warning(f"获取学生姓名失败: {e}")
                
                gift_result = await db.execute(
                    select(Gift).where(Gift.id == order.gift_id)
                )
                gift = gift_result.scalar_one_or_none()
                
                class_result = await db.execute(
                    select(ClassInfo).where(ClassInfo.id == order.class_id)
                )
                class_info = class_result.scalar_one_or_none()
                
                # 获取操作人信息
                operator_name = ""
                if order.operator_id:
                    try:
                        # 检查操作人是否是学员
                        from app.models.class_student import ClassStudent
                        from app.models.student_profile import StudentProfile
                        
                        # 查询该操作人是否在当前订单的班级中作为学员
                        student_result = await db.execute(
                            select(ClassStudent).join(StudentProfile).where(
                                StudentProfile.user_id == order.operator_id,
                                ClassStudent.class_id == order.class_id
                            )
                        )
                        student = student_result.scalar_one_or_none()
                        
                        if student:
                            # 如果是学员，使用班级中的名字
                            operator_name = student.name_in_class or ""
                        else:
                            # 否则使用用户注册的名字
                            operator_result = await db.execute(
                                select(User).where(User.id == order.operator_id)
                            )
                            operator = operator_result.scalar_one_or_none()
                            if operator:
                                operator_name = operator.real_name or operator.username or ""
                    except Exception as e:
                        logger.warning(f"获取操作人信息失败: {e}")
                
                order_list.append({
                    "id": order.id,
                    "student_name": student_name,
                    "gift_name": gift.name if gift else "",
                    "class_name": class_info.class_name if class_info else "",
                    "price": order.price,
                    "status": order.status,
                    "operator_name": operator_name,
                    "created_at": order.created_at,
                    "qr_code": order.qr_code  # 添加核销码
                })
            except Exception as e:
                logger.error(f"处理订单{order.id}失败: {e}")
                # 即使某个订单处理失败，也继续处理其他订单
                order_list.append({
                    "id": order.id,
                    "student_name": "",
                    "gift_name": "",
                    "class_name": "",
                    "price": order.price,
                    "status": order.status,
                    "operator_name": "",
                    "created_at": order.created_at
                })
        
        return {
            "items": order_list,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"获取订单列表失败: {e}")
        return {
            "items": [],
            "total": 0,
            "skip": skip,
            "limit": limit
        }


@router.get("/teacher")
async def get_teacher_orders(
    class_id: Optional[int] = Query(None),
    status: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    """获取导师的订单列表（兼容旧路径）"""
    return await get_orders(class_id, status, skip, limit, current_user, db)


@router.get("/completed")
async def get_completed_orders(
    class_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    """获取导师已完成订单列表（从历史记录读取）"""
    from app.models.gift_order_log import GiftOrderLog
    from app.models.class_student import ClassStudent
    from sqlalchemy import or_
    
    try:
        logger.info(f"Current user: {current_user.id}, role: {current_user.role.role_name if current_user.role else 'None'}")
        # 超级管理员和管理员可以查看所有订单
        if current_user.role and current_user.role.role_name in ["super_admin", "admin"]:
            logger.info("Admin user, querying all orders")
            query = select(GiftOrderLog)
        else:
            logger.info(f"Non-admin user, querying orders for teacher_id: {current_user.id}")
            query = select(GiftOrderLog).where(GiftOrderLog.teacher_id == current_user.id)
        
        # 查询已完成订单（状态为2已完成或3已取消）
        query = query.where(or_(GiftOrderLog.status == 2, GiftOrderLog.status == 3))
        logger.info(f"Query: {query}")
        
        if class_id:
            query = query.where(GiftOrderLog.class_id == class_id)
        
        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar() or 0
        
        query = query.order_by(GiftOrderLog.operated_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        order_logs = result.scalars().all()
        
        order_list = []
        for order_log in order_logs:
            # 获取礼品名称
            gift_result = await db.execute(
                select(Gift).where(Gift.id == order_log.gift_id)
            )
            gift = gift_result.scalar_one_or_none()
            
            # 获取班级信息
            class_result = await db.execute(
                select(ClassInfo).where(ClassInfo.id == order_log.class_id)
            )
            class_info = class_result.scalar_one_or_none()
            
            # 获取学员姓名
            student_name = ""
            from app.models.student_profile import StudentProfile
            from sqlalchemy.orm import selectinload
            student_class_result = await db.execute(
                select(ClassStudent).options(
                    selectinload(ClassStudent.student_profile).selectinload(StudentProfile.user)
                ).where(ClassStudent.id == order_log.class_student_id)
            )
            student_class = student_class_result.scalar_one_or_none()
            if student_class:
                try:
                    if student_class.student_profile and student_class.student_profile.user:
                        student_name = student_class.student_profile.user.real_name
                    else:
                        student_name = student_class.name_in_class or ""
                except Exception as e:
                    student_name = student_class.name_in_class if student_class else ""
                    logger.warning(f"获取学生姓名失败: {e}")
            
            # 获取操作人姓名
            operator_name = ""
            if order_log.operator_id:
                try:
                    operator_result = await db.execute(
                        select(User).where(User.id == order_log.operator_id)
                    )
                    operator = operator_result.scalar_one_or_none()
                    if operator:
                        operator_name = operator.real_name or operator.username or ""
                except Exception as e:
                    logger.warning(f"获取操作人信息失败: {e}")
            
            order_list.append({
                "id": order_log.order_id,
                "student_name": student_name,
                "gift_name": gift.name if gift else "",
                "class_name": class_info.class_name if class_info else "",
                "price": order_log.price,
                "status": order_log.status,
                "action": order_log.action,
                "operator_name": operator_name,
                "remarks": order_log.remarks or "",
                "operated_at": order_log.operated_at,
                "created_at": order_log.created_at
            })
        
        return {
            "items": order_list,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"获取已完成订单列表失败: {e}")
        return {
            "items": [],
            "total": 0,
            "skip": skip,
            "limit": limit
        }


@router.post("/{order_id}/approve")
async def approve_order(
    order_id: int,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    """审核通过订单"""
    result = await db.execute(
        select(GiftOrder).join(
            Gift, Gift.id == GiftOrder.gift_id
        ).where(
            GiftOrder.id == order_id,
            GiftOrder.teacher_id == current_user.id
        )
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )
    
    if order.status != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="订单状态不正确"
        )
    
    # 获取班级信息
    from app.models.class_info import ClassInfo
    class_result = await db.execute(
        select(ClassInfo).where(ClassInfo.id == order.class_id)
    )
    class_info = class_result.scalar_one_or_none()
    
    if not class_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="班级不存在"
        )
    
    # 更新订单状态
    order.status = 1
    order.operator_id = current_user.id  # 记录操作人
    order.updated_at = datetime.utcnow()
    
    try:
        await db.commit()
        await db.refresh(order)
        
        # 写入订单操作记录
        from app.models.gift_order_log import GiftOrderLog
        real_name = current_user.real_name or current_user.username
        order_log = GiftOrderLog(
            order_id=order.id,
            class_student_id=order.class_student_id,
            gift_id=order.gift_id,
            class_id=order.class_id,
            teacher_id=order.teacher_id,
            creator_id=order.creator_id,
            operator_id=current_user.id,
            price=order.price,
            status=order.status,
            qr_code=order.qr_code,
            action="approve",
            remarks=f"导师 {real_name} 审核通过订单"
        )
        db.add(order_log)
        await db.commit()
        
        logger.info(f"审核通过订单: {order.id}, 扣减成长值: {order.price}")
        return {"message": "审核通过成功"}
    except Exception as e:
        await db.rollback()
        logger.error(f"审核通过订单失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="审核通过失败，请稍后重试"
        )


@router.post("/{order_id}/verify")
async def verify_order(
    order_id: int,
    verify_data: VerifyOrder,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    """核销订单"""
    result = await db.execute(
        select(GiftOrder).join(
            Gift, Gift.id == GiftOrder.gift_id
        ).where(
            GiftOrder.id == order_id,
            GiftOrder.teacher_id == current_user.id,
            GiftOrder.status == 1,  # 待核销状态
            GiftOrder.qr_code == verify_data.qr_code  # 验证核销码
        )
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在或状态不正确"
        )
    
    # 检查是否已经核销
    from app.models.verify_record import VerifyRecord
    verify_result = await db.execute(
        select(VerifyRecord).where(VerifyRecord.order_id == order_id)
    )
    verify_record = verify_result.scalar_one_or_none()
    
    if verify_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="订单已核销"
        )
    
    # 更新订单状态
    order.status = 2  # 已核销
    order.operator_id = current_user.id  # 记录操作人
    order.updated_at = datetime.utcnow()
    
    # 创建核销记录
    verify_record = VerifyRecord(
        order_id=order.id,
        verify_user_id=current_user.id,
        class_id=order.class_id
    )
    db.add(verify_record)
    
    # 记录系统日志
    from app.models.system_log import SystemLog, LogType, LogLevel
    import json
    
    # 确保 real_name 不为 None
    real_name = current_user.real_name or current_user.username
    
    system_log = SystemLog(
        user_id=current_user.id,
        username=current_user.username,
        real_name=real_name,
        log_type=LogType.UPDATE,
        log_level=LogLevel.INFO,
        module="订单管理",
        action="核销订单",
        request_params=f"{{\"order_id\": {order.id}, \"student_id\": {order.class_student_id}, \"gift_id\": {order.gift_id}}}"
    )
    db.add(system_log)
    
    try:
        await db.commit()
        await db.refresh(order)
        
        # 写入订单操作记录
        from app.models.gift_order_log import GiftOrderLog
        order_log = GiftOrderLog(
            order_id=order.id,
            class_student_id=order.class_student_id,
            gift_id=order.gift_id,
            class_id=order.class_id,
            teacher_id=order.teacher_id,
            creator_id=order.creator_id,
            operator_id=current_user.id,
            price=order.price,
            status=order.status,
            qr_code=order.qr_code,
            action="verify",
            remarks=f"导师 {real_name} 核销订单"
        )
        db.add(order_log)
        await db.commit()
        
        logger.info(f"导师 {real_name} 核销订单: {order.id}")
        return {
            "id": order.id,
            "status": order.status,
            "verify_time": verify_record.verify_time
        }
    except Exception as e:
        await db.rollback()
        logger.error(f"核销订单失败: {e}")
        import traceback
        logger.error(f"错误堆栈: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="核销订单失败，请稍后重试"
        )


@router.post("/{order_id}/reject")
async def reject_order(
    order_id: int,
    reject_data: OrderReject,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    """拒绝订单"""
    result = await db.execute(
        select(GiftOrder).where(
            GiftOrder.id == order_id,
            GiftOrder.teacher_id == current_user.id
        )
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )
    
    if order.status != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="订单状态不正确"
        )
    
    # 获取班级信息
    from app.models.class_info import ClassInfo
    class_result = await db.execute(
        select(ClassInfo).where(ClassInfo.id == order.class_id)
    )
    class_info = class_result.scalar_one_or_none()
    
    if not class_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="班级不存在"
        )
    
    order.status = 3  # 已取消
    order.cancel_reason = reject_data.reason
    order.operator_id = current_user.id  # 记录操作人
    order.updated_at = datetime.utcnow()
    
    gift_result = await db.execute(
        select(Gift).where(Gift.id == order.gift_id)
    )
    gift = gift_result.scalar_one_or_none()
    
    if gift:
        stock_result = await db.execute(
            select(GiftStock).where(GiftStock.gift_id == gift.id)
        )
        gift_stock = stock_result.scalar_one_or_none()
        
        if gift_stock:
            gift_stock.current_stock += 1
            gift_stock.total_out_stock -= 1
    
    # 恢复学员的成长值
    from app.models.class_student import ClassStudent
    from app.models.growth_log import Growth
    
    # 查询ClassStudent信息
    student_result = await db.execute(
        select(ClassStudent).where(ClassStudent.id == order.class_student_id)
    )
    student = student_result.scalar_one_or_none()
    
    if student:
        # 添加成长值恢复记录
        growth_log = Growth(
            user_id=None,
            class_student_id=student.id,
            class_id=order.class_id,
            teacher_id=current_user.id,
            change_value=order.price,
            reason=f"订单拒绝：恢复兑换礼品消耗的成长值",
            operator_id=current_user.id,
            input_type=1,  # 手动录入
            class_status=class_info.status
        )
        db.add(growth_log)
    
    # 记录系统日志
    from app.models.system_log import SystemLog, LogType, LogLevel
    system_log = SystemLog(
        user_id=current_user.id,
        username=current_user.username,
        real_name=current_user.real_name,
        log_type=LogType.UPDATE,
        log_level=LogLevel.INFO,
        module="订单管理",
        action="拒绝订单",
        request_params=f"{{\"order_id\": {order_id}, \"reason\": \"{reject_data.reason}\", \"student_id\": {order.class_student_id}, \"gift_id\": {order.gift_id}, \"price\": {order.price}}}"
    )
    db.add(system_log)
    
    try:
        await db.commit()
        
        # 写入订单操作记录
        from app.models.gift_order_log import GiftOrderLog
        real_name = current_user.real_name or current_user.username
        order_log = GiftOrderLog(
            order_id=order.id,
            class_student_id=order.class_student_id,
            gift_id=order.gift_id,
            class_id=order.class_id,
            teacher_id=order.teacher_id,
            creator_id=order.creator_id,
            operator_id=current_user.id,
            price=order.price,
            status=order.status,
            qr_code=order.qr_code,
            action="reject",
            remarks=f"导师 {real_name} 拒绝订单，原因: {reject_data.reason}"
        )
        db.add(order_log)
        await db.commit()
        
        logger.info(f"拒绝订单: {order.id}, 原因: {reject_data.reason}")
        return {"message": "拒绝成功"}
    except Exception as e:
        await db.rollback()
        logger.error(f"拒绝订单失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="拒绝订单失败，请稍后重试"
        )


@router.post("/")
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建兑换订单"""
    # 检查用户角色，只有学员可以创建订单
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有学员可以兑换奖励"
        )
    
    # 检查数量是否为正整数
    quantity = order_data.quantity if order_data.quantity else 1
    if not isinstance(quantity, int) or quantity < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="兑换份数必须为正整数"
        )
    
    # 检查礼品是否存在
    gift_result = await db.execute(
        select(Gift).where(Gift.id == order_data.gift_id)
    )
    gift = gift_result.scalar_one_or_none()
    
    if not gift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="礼品不存在"
        )
    
    if not gift.status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="礼品已下架"
        )
    
    # 检查礼品库存
    stock_result = await db.execute(
        select(GiftStock).where(GiftStock.gift_id == gift.id)
    )
    gift_stock = stock_result.scalar_one_or_none()
    
    if not gift_stock or gift_stock.current_stock < quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"礼品库存不足，当前库存: {gift_stock.current_stock if gift_stock else 0}"
        )
    
    # 检查班级是否存在且状态正常
    class_result = await db.execute(
        select(ClassInfo).where(ClassInfo.id == order_data.class_id)
    )
    class_info = class_result.scalar_one_or_none()
    
    if not class_info or not class_info.status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="班级不存在或已关闭"
        )
    
    # 检查学员是否绑定了该班级
    from app.models.class_student import ClassStudent, BindStatus
    from app.models.student_profile import StudentProfile
    student_class_result = await db.execute(
        select(ClassStudent).join(StudentProfile).where(
            StudentProfile.user_id == current_user.id,
            ClassStudent.class_id == order_data.class_id,
            ClassStudent.bind_status == BindStatus.APPROVED
        )
    )
    student_class = student_class_result.scalar_one_or_none()
    
    if not student_class:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您未绑定该班级"
        )
    
    # 计算总价格
    total_price = gift.price * quantity
    
    # 检查学员成长值是否足够
    from app.models.growth_log import Growth
    from sqlalchemy import func
    growth_log_result = await db.execute(
        select(func.sum(Growth.change_value)).where(
            Growth.class_student_id == student_class.id
        )
    )
    available_score = growth_log_result.scalar() or 0
    
    if available_score < total_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"成长值不足，需要: {total_price}, 可用: {available_score}"
        )
    
    # 学员创建的订单，状态为待审核
    order_status = 0
    
    # 创建订单（不立即提交）
    logger.info(f"[DEBUG] 创建订单 - student_class.id: {student_class.id}, gift.id: {gift.id}, class_id: {order_data.class_id}, teacher_id: {class_info.teacher_id}, price: {total_price}, quantity: {quantity}, status: {order_status}")
    order = GiftOrder(
        class_student_id=student_class.id,
        gift_id=gift.id,
        class_id=order_data.class_id,
        teacher_id=class_info.teacher_id,
        creator_id=current_user.id,  # 记录创建人
        operator_id=current_user.id,  # 记录操作人
        price=total_price,
        status=order_status,
        qr_code=f"order_{student_class.id}_{gift.id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
    )
    db.add(order)
    
    # 记录系统日志
    from app.models.system_log import SystemLog, LogType, LogLevel
    import json
    
    # 确保 real_name 不为 None
    real_name = current_user.real_name or current_user.username
    
    system_log = SystemLog(
        user_id=current_user.id,
        username=current_user.username,
        real_name=real_name,
        log_type=LogType.CREATE.value,  # 使用枚举值
        log_level=LogLevel.INFO.value,  # 使用枚举值
        module="订单管理",
        action="创建订单",
        request_params=json.dumps({
            "gift_id": gift.id,
            "class_id": order_data.class_id,
            "student_id": student_class.id,
            "price": total_price,
            "quantity": quantity
        })
    )
    db.add(system_log)
    
    # 扣减库存
    from sqlalchemy import update
    
    # 直接更新库存
    update_result = await db.execute(
        update(GiftStock)
        .where(
            GiftStock.gift_id == gift.id,
            GiftStock.current_stock >= quantity  # 确保库存足够
        )
        .values(
            current_stock=GiftStock.current_stock - quantity,
            total_out_stock=GiftStock.total_out_stock + quantity
        )
    )
    
    # 扣减成长值
    growth_log = Growth(
        user_id=None,
        class_student_id=student_class.id,
        class_id=order_data.class_id,
        teacher_id=class_info.teacher_id,
        change_value=-total_price,
        reason=f"兑换礼品：{gift.name} x {quantity}（待审核）",
        operator_id=current_user.id,
        input_type=1,  # 手动录入
        class_status=class_info.status
    )
    db.add(growth_log)
    
    # 检查更新是否成功
    if update_result.rowcount == 0:
        await db.rollback()  # 回滚订单创建
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="库存不足"
        )
    
    try:
        await db.commit()
        await db.refresh(order)
        
        # 写入订单操作记录
        from app.models.gift_order_log import GiftOrderLog
        order_log = GiftOrderLog(
            order_id=order.id,
            class_student_id=order.class_student_id,
            gift_id=order.gift_id,
            class_id=order.class_id,
            teacher_id=order.teacher_id,
            creator_id=order.creator_id,
            operator_id=order.operator_id,
            price=order.price,
            status=order.status,
            qr_code=order.qr_code,
            action="create",
            remarks=f"学员 {real_name} 创建订单，兑换 {gift.name} x {quantity}"
        )
        db.add(order_log)
        await db.commit()
        
        logger.info(f"学员 {real_name} 兑换礼品: {gift.name} x {quantity}, 消耗成长值: {total_price}")
        return {
            "id": order.id,
            "gift_id": order.gift_id,
            "gift_name": gift.name,
            "cost_score": order.price,
            "quantity": quantity,
            "status": order.status,
            "created_at": order.created_at
        }
    except Exception as e:
        await db.rollback()
        logger.error(f"创建订单失败: {e}")
        import traceback
        logger.error(f"错误堆栈: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建订单失败，请稍后重试"
        )


@router.get("/user")
async def get_user_orders(
    status: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取学员的订单列表"""
    from app.models.class_student import ClassStudent
    from app.models.student_profile import StudentProfile
    from sqlalchemy.orm import selectinload
    
    # 检查用户是否是学员
    student_class_result = await db.execute(
        select(ClassStudent).join(StudentProfile).where(
            StudentProfile.user_id == current_user.id
        )
    )
    student_classes = student_class_result.scalars().all()
    
    if student_classes:
        # 学员只能查看自己的订单
        student_class_ids = [sc.id for sc in student_classes]
        query = select(GiftOrder).where(GiftOrder.class_student_id.in_(student_class_ids))
    else:
        # 导师只能查看自己班级的订单
        query = select(GiftOrder).where(GiftOrder.teacher_id == current_user.id)
    
    if status:
        query = query.where(GiftOrder.status == status)
    
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0
    
    query = query.order_by(GiftOrder.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    orders = result.scalars().all()
    
    order_list = []
    for order in orders:
        # 使用 selectinload 预加载关系
        gift_result = await db.execute(
            select(Gift).where(Gift.id == order.gift_id)
        )
        gift = gift_result.scalar_one_or_none()
        
        class_result = await db.execute(
            select(ClassInfo).where(ClassInfo.id == order.class_id)
        )
        class_info = class_result.scalar_one_or_none()
        
        # 获取学生信息，使用 selectinload 预加载
        student_name = ""
        class_student_result = await db.execute(
            select(ClassStudent).options(
                selectinload(ClassStudent.student_profile).selectinload(StudentProfile.user)
            ).where(ClassStudent.id == order.class_student_id)
        )
        class_student = class_student_result.scalar_one_or_none()
        if class_student:
            if class_student.student_profile and class_student.student_profile.user:
                student_name = class_student.student_profile.user.real_name
            else:
                student_name = class_student.name_in_class or ""
        
        order_list.append({
            "id": order.id,
            "gift_name": gift.name if gift else "",
            "class_name": class_info.class_name if class_info else "",
            "student_name": student_name,
            "price": order.price,
            "status": order.status,
            "status_text": "待审核" if order.status == 0 else "待核销" if order.status == 1 else "已完成",
            "created_at": order.created_at,
            "qr_code": order.qr_code  # 添加核销码
        })
    
    return {
        "items": order_list,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.post("/teacher")
async def create_teacher_order(
    order_data: dict,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    """导师为学生兑换奖励"""
    gift_id = order_data.get("gift_id")
    class_id = order_data.get("class_id")
    user_id = order_data.get("user_id")
    quantity = order_data.get("quantity", 1)
    
    if not gift_id or not class_id or not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="缺少必要参数"
        )
    
    # 检查数量是否为正整数
    if not isinstance(quantity, int) or quantity < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="兑换份数必须为正整数"
        )
    
    # 检查礼品是否存在
    gift_result = await db.execute(
        select(Gift).where(Gift.id == gift_id)
    )
    gift = gift_result.scalar_one_or_none()
    
    if not gift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="礼品不存在"
        )
    
    if not gift.status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="礼品已下架"
        )
    
    # 检查礼品库存
    stock_result = await db.execute(
        select(GiftStock).where(GiftStock.gift_id == gift.id)
    )
    gift_stock = stock_result.scalar_one_or_none()
    
    if not gift_stock or gift_stock.current_stock < quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="礼品库存不足"
        )
    
    # 检查班级是否存在且状态正常
    class_result = await db.execute(
        select(ClassInfo).where(ClassInfo.id == class_id)
    )
    class_info = class_result.scalar_one_or_none()
    
    if not class_info or not class_info.status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="班级不存在或已关闭"
        )
    
    # 检查学员是否在该班级中
    from app.models.class_student import ClassStudent
    
    # 处理 user_id 参数
    student_class = None
    if isinstance(user_id, str) and user_id.startswith('temp_'):
        # 临时ID格式：temp_{class_student_id}
        try:
            class_student_id = int(user_id.split('_')[1])
            student_class_result = await db.execute(
                select(ClassStudent).where(
                    ClassStudent.id == class_student_id,
                    ClassStudent.class_id == class_id
                )
            )
            student_class = student_class_result.scalar_one_or_none()
        except (ValueError, IndexError):
            pass
    else:
        # 尝试两种方式查找：1. 直接使用 user_id 作为 ClassStudent.id
        # 2. 通过 student_profile.user_id 查找
        student_class_result = await db.execute(
            select(ClassStudent).where(
                ClassStudent.class_id == class_id,
                ClassStudent.id == user_id
            )
        )
        student_class = student_class_result.scalar_one_or_none()
        
        if not student_class:
            # 尝试通过 student_profile.user_id 查找
            student_class_result = await db.execute(
                select(ClassStudent).where(
                    ClassStudent.class_id == class_id,
                    ClassStudent.student_profile.has(user_id=user_id)
                )
            )
            student_class = student_class_result.scalar_one_or_none()
    
    if not student_class:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="学生不在该班级中"
        )
    
    # 检查学员成长值是否足够
    from app.models.growth_log import Growth
    from sqlalchemy import func
    
    # 从Growth表计算成长值，使用student_class.id作为唯一标识
    growth_log_result = await db.execute(
        select(func.sum(Growth.change_value)).where(
            Growth.class_student_id == student_class.id
        )
    )
    available_score = growth_log_result.scalar() or 0
    
    total_cost = gift.price * quantity
    if available_score < total_cost:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="学生成长值不足"
        )
    
    # 扣减成长值，使用student_class.id作为唯一标识
    growth_log = Growth(
        user_id=None,
        class_student_id=student_class.id,
        class_id=class_id,
        teacher_id=current_user.id,
        change_value=-total_cost,
        reason=f"兑换礼品：{gift.name} x {quantity}",
        operator_id=current_user.id,
        input_type=1,  # 手动录入
        class_status=class_info.status
    )
    db.add(growth_log)
    
    # 扣减库存
    from sqlalchemy import update
    
    # 直接更新库存
    update_result = await db.execute(
        update(GiftStock)
        .where(
            GiftStock.gift_id == gift.id,
            GiftStock.current_stock >= quantity  # 确保库存足够
        )
        .values(
            current_stock=GiftStock.current_stock - quantity,
            total_out_stock=GiftStock.total_out_stock + quantity
        )
    )
    
    # 检查更新是否成功
    if update_result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="库存更新失败，请稍后重试"
        )
    
    # 创建订单
    # 使用student_class.id作为唯一标识
    qr_code_user_id = f"student_{student_class.id}"
    # 生成唯一的二维码标识
    qr_code = f"order_{qr_code_user_id}_{gift.id}_{datetime.utcnow().timestamp()}"
    # 使用student_class.id作为class_student_id
    order = GiftOrder(
        class_student_id=student_class.id,
        gift_id=gift.id,
        class_id=class_id,
        teacher_id=current_user.id,
        creator_id=current_user.id,  # 记录创建人（导师）
        operator_id=current_user.id,  # 记录操作人
        price=total_cost,
        status=2,  # 导师直接兑换，状态为已完成，不需要核销
        qr_code=qr_code
    )
    db.add(order)
    
    # 记录系统日志
    from app.models.system_log import SystemLog, LogType, LogLevel
    import json
    # 构建请求参数字符串
    request_params = json.dumps({
        "gift_id": gift.id,
        "class_id": class_id,
        "student_id": student_class.id,
        "quantity": quantity,
        "total_cost": total_cost
    })
    system_log = SystemLog(
        user_id=current_user.id,
        username=current_user.username,
        real_name=current_user.real_name,
        log_type=LogType.CREATE.value,  # 使用枚举值
        log_level=LogLevel.INFO.value,  # 使用枚举值
        module="订单管理",
        action="导师为学生兑换礼品",
        request_params=request_params
    )
    db.add(system_log)
    
    try:
        await db.commit()
        await db.refresh(order)
        
        # 获取学生姓名
        student_name = ""
        if student_class.student_profile and student_class.student_profile.user:
            student_name = student_class.student_profile.user.real_name
        else:
            student_name = student_class.name_in_class
        
        # 写入订单操作记录
        from app.models.gift_order_log import GiftOrderLog
        real_name = current_user.real_name or current_user.username
        order_log = GiftOrderLog(
            order_id=order.id,
            class_student_id=order.class_student_id,
            gift_id=order.gift_id,
            class_id=order.class_id,
            teacher_id=order.teacher_id,
            creator_id=order.creator_id,
            operator_id=order.operator_id,
            price=order.price,
            status=order.status,
            qr_code=order.qr_code,
            action="create",
            remarks=f"导师 {real_name} 为学生 {student_name} 创建订单，兑换 {gift.name} x {quantity}"
        )
        db.add(order_log)
        await db.commit()
        
        logger.info(f"导师 {current_user.real_name} 为学生 {student_name} 兑换礼品: {gift.name} x {quantity}, 消耗成长值: {total_cost}")
        
        return {
            "id": order.id,
            "gift_id": order.gift_id,
            "gift_name": gift.name,
            "cost_score": order.price,
            "status": order.status,
            "created_at": order.created_at
        }
    except Exception as e:
        await db.rollback()
        logger.error(f"导师为学生兑换礼品失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="兑换礼品失败，请稍后重试"
        )
