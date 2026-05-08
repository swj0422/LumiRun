from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from app.core.database import get_db
from app.core.security import require_admin
from app.models.user import User
from app.models.gift_order import GiftOrder
from app.models.gift import Gift
from app.models.class_student import ClassStudent
from app.models.class_info import ClassInfo
from sqlalchemy.orm import selectinload

router = APIRouter()


@router.get("/orders")
async def get_admin_orders(
    order_no: Optional[str] = Query(None, description="订单号"),
    class_id: Optional[int] = Query(None, description="班级ID"),
    student_id: Optional[int] = Query(None, description="学员ID"),
    status: Optional[int] = Query(None, description="订单状态"),
    gift_name: Optional[str] = Query(None, description="礼品名称"),
    start_time: Optional[str] = Query(None, description="开始时间"),
    end_time: Optional[str] = Query(None, description="结束时间"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    query = select(GiftOrder).options(
        selectinload(GiftOrder.gift),
        selectinload(GiftOrder.class_student).selectinload(ClassStudent.class_info)
    )
    
    if order_no:
        query = query.where(GiftOrder.qr_code.contains(order_no))
    if class_id:
        query = query.where(GiftOrder.class_id == class_id)
    if student_id:
        query = query.where(GiftOrder.class_student_id == student_id)
    if status is not None:
        query = query.where(GiftOrder.status == status)
    if gift_name:
        query = query.join(Gift).where(Gift.name.contains(gift_name))
    if start_time:
        query = query.where(GiftOrder.created_at >= start_time)
    if end_time:
        query = query.where(GiftOrder.created_at <= end_time)
    
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0
    
    query = query.order_by(GiftOrder.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    orders = result.scalars().all()
    
    order_list = []
    for order in orders:
        gift_name = order.gift.name if order.gift else "-"
        student_name = order.class_student.name_in_class if order.class_student else "-"
        class_name = order.class_student.class_info.class_name if order.class_student and order.class_student.class_info else "-"
        
        order_list.append({
            "id": order.id,
            "order_no": order.qr_code,
            "class_id": order.class_id,
            "class_name": class_name,
            "class_student_id": order.class_student_id,
            "student_name": student_name,
            "gift_id": order.gift_id,
            "gift_name": gift_name,
            "gift_price": order.gift.price if order.gift else 0,
            "quantity": 1,
            "total_price": order.price,
            "points_cost": order.price,
            "verify_code": order.qr_code,
            "status": order.status,
            "created_at": order.created_at,
            "updated_at": order.updated_at
        })
    
    return {
        "items": order_list,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/orders/{order_id}")
async def get_order_detail(
    order_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    order = await db.execute(
        select(GiftOrder)
        .options(
            selectinload(GiftOrder.gift),
            selectinload(GiftOrder.class_student).selectinload(ClassStudent.class_info)
        )
        .where(GiftOrder.id == order_id)
    )
    order = order.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )
    
    gift_name = order.gift.name if order.gift else "-"
    gift_image_url = order.gift.image_url if order.gift else ""
    student_name = order.class_student.name_in_class if order.class_student else "-"
    class_name = order.class_student.class_info.class_name if order.class_student and order.class_student.class_info else "-"
    
    return {
        "id": order.id,
        "order_no": order.qr_code,
        "class_id": order.class_id,
        "class_name": class_name,
        "class_student_id": order.class_student_id,
        "student_name": student_name,
        "gift_id": order.gift_id,
        "gift_name": gift_name,
        "gift_description": order.gift.description if order.gift else "",
        "gift_image_url": gift_image_url,
        "gift_price": order.gift.price if order.gift else 0,
        "quantity": 1,
        "total_price": order.price,
        "status": order.status,
        "created_at": order.created_at,
        "updated_at": order.updated_at
    }


@router.put("/orders/{order_id}/status")
async def update_order_status(
    order_id: int,
    status: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    from app.models.system_log import SystemLog, LogType, LogLevel
    
    order = await db.get(GiftOrder, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )
    
    old_status = order.status
    order.status = status
    
    system_log = SystemLog(
        user_id=current_user.id,
        username=current_user.username,
        real_name=current_user.real_name,
        log_type=LogType.UPDATE,
        log_level=LogLevel.INFO,
        module="订单管理",
        action="更新订单状态",
        biz_type="order",
        biz_id=order_id,
        request_params=f'{{"order_id": {order_id}, "status": {status}}}',
        before_data=f'{{"订单号": "{order.qr_code}", "原状态": {old_status}, "新状态": {status}}}'
    )
    db.add(system_log)
    
    await db.commit()
    
    return {"message": "状态更新成功"}


@router.delete("/orders/{order_id}")
async def delete_order(
    order_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    from app.models.system_log import SystemLog, LogType, LogLevel
    
    order = await db.get(GiftOrder, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )
    
    order_no = order.qr_code
    total_price = order.price
    
    await db.delete(order)
    
    system_log = SystemLog(
        user_id=current_user.id,
        username=current_user.username,
        real_name=current_user.real_name,
        log_type=LogType.DELETE,
        log_level=LogLevel.INFO,
        module="订单管理",
        action="删除订单",
        biz_type="order",
        biz_id=order_id,
        request_params=f'{{"order_id": {order_id}}}',
        before_data=f'{{"订单号": "{order_no}", "总价": {total_price}}}'
    )
    db.add(system_log)
    
    await db.commit()
    
    return {"message": "删除成功"}
