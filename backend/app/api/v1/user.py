from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List
from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.schemas.user import UserCreate, UserUpdate, UserResponse, PasswordChange
from app.services.user_service import UserService
from app.models.user import User
from app.models.class_info import ClassInfo
from app.models.class_student import ClassStudent
from app.models.gift import Gift
from app.models.gift_order import GiftOrder

router = APIRouter()


@router.get("/stats")
async def get_teacher_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取导师统计数据"""
    from app.models.class_student import ClassStudent
    
    # 统计导师的班级数量
    class_count = await db.execute(
        select(func.count(ClassInfo.id)).where(ClassInfo.teacher_id == current_user.id)
    )
    
    # 统计导师所有班级的学员数量（只统计ClassStudent表，排除已删除的）
    student_count = await db.execute(
        select(func.count(ClassStudent.id)).join(
            ClassInfo, ClassInfo.id == ClassStudent.class_id
        ).where(
            ClassInfo.teacher_id == current_user.id,
            ClassStudent.is_deleted == False
        )
    )
    
    # 统计导师创建的奖励数量
    gift_count = await db.execute(
        select(func.count(Gift.id)).where(Gift.teacher_id == current_user.id)
    )
    
    # 统计导师的待核销订单数量
    pending_order_count = await db.execute(
        select(func.count(GiftOrder.id)).join(
            Gift, Gift.id == GiftOrder.gift_id
        ).where(
            Gift.teacher_id == current_user.id,
            GiftOrder.status == 0
        )
    )
    
    return {
        "classCount": class_count.scalar() or 0,
        "studentCount": student_count.scalar() or 0,
        "giftCount": gift_count.scalar() or 0,
        "pendingOrderCount": pending_order_count.scalar() or 0
    }


@router.get("/", response_model=dict)
async def get_users(
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
            "username": user.username,
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


@router.get("/{user_id}", response_model=dict)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取用户详情"""
    # 权限检查：管理员可查看所有用户，其他用户只能查看自己
    if current_user.role.role_name not in ["super_admin", "admin"] and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限查看此用户信息"
        )
    
    user = await UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    role = await UserService.get_role_by_id(db, user.role_id)
    
    return {
        "id": user.id,
        "username": user.username,
        "real_name": user.real_name,
        "phone": user.phone,
        "role_id": user.role_id,
        "role_name": role.role_name if role else "未知",
        "status": user.status,
        "last_login_time": user.last_login_time,
        "login_count": user.login_count,
        "created_at": user.created_at
    }


@router.post("/", response_model=dict)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """创建用户（管理员）"""
    try:
        user = await UserService.create_user(db, user_data, is_approved=True)
        return {
            "message": "用户创建成功",
            "user_id": user.id
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/password", response_model=dict)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """修改密码"""
    try:
        await UserService.change_password(
            db, current_user,
            password_data.old_password,
            password_data.new_password
        )
        return {
            "message": "密码修改成功"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{user_id}", response_model=dict)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新用户信息"""
    # 权限检查：管理员可更新所有用户，其他用户只能更新自己
    if current_user.role.role_name not in ["super_admin", "admin"] and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限更新此用户信息"
        )
    
    user = await UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    try:
        user = await UserService.update_user(db, user, user_data)
        return {
            "message": "用户信息更新成功",
            "user_id": user.id
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{user_id}/approve", response_model=dict)
async def approve_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """审核通过用户（导师注册）"""
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


@router.put("/{user_id}/disable", response_model=dict)
async def disable_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """禁用/启用用户"""
    try:
        user = await UserService.disable_user(db, user_id)
        action = "启用" if user.status else "禁用"
        return {
            "message": f"用户{action}成功",
            "user_id": user.id,
            "status": user.status
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
