from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.services.user_service import UserService
from app.models.user import User
from app.models.class_info import ClassInfo
from app.models.gift_order import GiftOrder
from app.api.v1 import admin_class, admin_student, admin_gift, admin_order, admin_suggestion

router = APIRouter()

router.include_router(admin_class.router, prefix="", tags=["班级管理"])
router.include_router(admin_student.router, prefix="", tags=["学员管理"])
router.include_router(admin_gift.router, prefix="", tags=["礼品管理"])
router.include_router(admin_order.router, prefix="", tags=["订单管理"])
router.include_router(admin_suggestion.router, prefix="", tags=["意见征集"])


@router.get("/stats")
async def get_admin_stats(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取管理员统计数据"""
    user_count = await db.execute(select(func.count(User.id)))
    class_count = await db.execute(select(func.count(ClassInfo.id)))
    pending_teacher_count = await db.execute(
        select(func.count(User.id)).where(User.role_id == 3, User.status == False)
    )
    pending_order_count = await db.execute(
        select(func.count(GiftOrder.id)).where(GiftOrder.status == 0)
    )
    
    return {
        "userCount": user_count.scalar() or 0,
        "classCount": class_count.scalar() or 0,
        "pendingTeacherCount": pending_teacher_count.scalar() or 0,
        "pendingOrderCount": pending_order_count.scalar() or 0
    }


@router.get("/users")
async def get_admin_users(
    role_id: Optional[int] = Query(None, description="角色ID"),
    status: Optional[bool] = Query(None, description="账号状态"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取用户列表（管理员）"""
    users, total = await UserService.get_users(db, role_id, status, keyword, skip, limit)
    
    user_list = []
    for user in users:
        role = await UserService.get_role_by_id(db, user.role_id)
        user_list.append({
            "id": user.id,
            "email": user.email,
            "real_name": user.real_name,
            "phone": user.phone,
            "role_id": user.role_id,
            "role_name": role.role_name if role else "未知",
            "status": user.status,
            "created_at": user.created_at
        })
    
    return {
        "items": user_list,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.post("/users/{user_id}/approve")
async def approve_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """审核通过用户（导师注册）"""
    # 超级管理员不能操作自己
    if current_user.role_id == 1 and current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="超级管理员不能操作自己的账号"
        )
    
    try:
        user = await UserService.approve_user(db, user_id)
        return {
            "message": "用户审核通过",
            "user_id": user.id
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/users/{user_id}/reject")
async def reject_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """拒绝用户注册申请"""
    # 超级管理员不能操作自己
    if current_user.role_id == 1 and current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="超级管理员不能操作自己的账号"
        )
    
    user = await UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    await UserService.delete_user(db, user_id)
    return {
        "message": "已拒绝该用户注册申请"
    }


@router.post("/users/{user_id}/disable")
async def disable_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """禁用用户"""
    # 超级管理员不能操作自己
    if current_user.role_id == 1 and current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="超级管理员不能操作自己的账号"
        )
    
    try:
        user = await UserService.disable_user(db, user_id)
        return {
            "message": "用户禁用成功",
            "user_id": user.id,
            "status": user.status
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/users/{user_id}/enable")
async def enable_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """启用用户"""
    # 超级管理员不能操作自己
    if current_user.role_id == 1 and current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="超级管理员不能操作自己的账号"
        )
    
    user = await UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    user.status = True
    await db.commit()
    return {
        "message": "用户启用成功",
        "user_id": user.id,
        "status": user.status
    }
