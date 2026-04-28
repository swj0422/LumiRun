from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List, Dict, Any
from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.models.user import User, Role
from app.models.permission import Permission, RolePermission
from app.services.permission_service import PermissionService

router = APIRouter()


@router.get("/roles")
async def get_roles(
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取角色列表"""
    query = select(Role)
    if keyword:
        query = query.where(Role.role_name.contains(keyword) | Role.remark.contains(keyword))
    
    result = await db.execute(query)
    roles = result.scalars().all()
    
    role_list = []
    for role in roles:
        role_list.append({
            "id": role.id,
            "role_name": role.role_name,
            "parent_id": role.parent_id,
            "remark": role.remark
        })
    
    return {
        "items": role_list,
        "total": len(role_list)
    }


@router.post("/roles")
async def create_role(
    role_data: dict,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """创建角色"""
    role_name = role_data.get("role_name")
    parent_id = role_data.get("parent_id")
    remark = role_data.get("remark")
    
    if not role_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="角色名称不能为空"
        )
    
    # 检查角色名称是否已存在
    existing_role = await db.execute(
        select(Role).where(Role.role_name == role_name)
    )
    if existing_role.scalar():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="角色名称已存在"
        )
    
    # 检查父角色是否存在
    if parent_id:
        parent_role = await db.get(Role, parent_id)
        if not parent_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="父角色不存在"
            )
    
    new_role = Role(
        role_name=role_name,
        parent_id=parent_id,
        remark=remark
    )
    
    db.add(new_role)
    await db.commit()
    await db.refresh(new_role)
    
    return {
        "message": "角色创建成功",
        "role_id": new_role.id
    }


@router.put("/roles/{role_id}")
async def update_role(
    role_id: int,
    role_data: dict,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """更新角色"""
    # 不允许编辑系统内置角色
    if role_id in [1, 2, 3, 4]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="系统内置角色不能编辑"
        )
    
    role = await db.execute(
        select(Role).where(Role.id == role_id)
    )
    role = role.scalar()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    role_name = role_data.get("role_name")
    parent_id = role_data.get("parent_id")
    remark = role_data.get("remark")
    
    if role_name:
        # 检查角色名称是否已存在（排除当前角色）
        existing_role = await db.execute(
            select(Role).where(Role.role_name == role_name, Role.id != role_id)
        )
        if existing_role.scalar():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="角色名称已存在"
            )
        role.role_name = role_name
    
    if parent_id is not None:
        # 检查父角色是否存在
        if parent_id:
            parent_role = await db.get(Role, parent_id)
            if not parent_role:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="父角色不存在"
                )
        role.parent_id = parent_id
    
    if remark is not None:
        role.remark = remark
    
    await db.commit()
    await db.refresh(role)
    
    return {
        "message": "角色更新成功",
        "role_id": role.id
    }


@router.delete("/roles/{role_id}")
async def delete_role(
    role_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """删除角色"""
    # 不允许删除系统内置角色
    if role_id in [1, 2, 3, 4]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="系统内置角色不能删除"
        )
    
    role = await db.execute(
        select(Role).where(Role.id == role_id)
    )
    role = role.scalar()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    # 检查是否有用户使用此角色
    users_with_role = await db.execute(
        select(User).where(User.role_id == role_id)
    )
    if users_with_role.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="此角色下有用户，不能删除"
        )
    
    # 删除角色权限关联
    role_permissions = await db.execute(
        select(RolePermission).where(RolePermission.role_id == role_id)
    )
    for rp in role_permissions.scalars():
        await db.delete(rp)
    
    await db.delete(role)
    await db.commit()
    
    return {
        "message": "角色删除成功"
    }


@router.get("/permissions")
async def get_permissions(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取权限列表"""
    result = await db.execute(select(Permission))
    permissions = result.scalars().all()
    
    permission_list = []
    for permission in permissions:
        permission_list.append({
            "id": permission.id,
            "permission_name": permission.permission_name,
            "permission_code": permission.permission_code,
            "parent_id": permission.parent_id,
            "type": permission.type,
            "path": permission.path,
            "component": permission.component,
            "icon": permission.icon,
            "sort": permission.sort,
            "status": permission.status
        })
    
    return {
        "items": permission_list,
        "total": len(permission_list)
    }


@router.post("/roles/{role_id}/permissions")
async def assign_permissions(
    role_id: int,
    permission_ids: List[int],
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """为角色分配权限"""
    role = await db.execute(
        select(Role).where(Role.id == role_id)
    )
    role = role.scalar()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    # 删除原有的权限关联
    existing_permissions = await db.execute(
        select(RolePermission).where(RolePermission.role_id == role_id)
    )
    for rp in existing_permissions.scalars():
        await db.delete(rp)
    
    # 添加新的权限关联
    for permission_id in permission_ids:
        # 检查权限是否存在
        permission = await db.execute(
            select(Permission).where(Permission.id == permission_id)
        )
        if not permission.scalar():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"权限ID {permission_id} 不存在"
            )
        
        new_rp = RolePermission(
            role_id=role_id,
            permission_id=permission_id
        )
        db.add(new_rp)
    
    await db.commit()
    
    return {
        "message": "权限分配成功"
    }


@router.get("/roles/{role_id}/permissions")
async def get_role_permissions(
    role_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取角色的权限列表"""
    role = await db.execute(
        select(Role).where(Role.id == role_id)
    )
    role = role.scalar()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    role_permissions = await db.execute(
        select(RolePermission).where(RolePermission.role_id == role_id)
    )
    permission_ids = [rp.permission_id for rp in role_permissions.scalars()]
    
    return {
        "permission_ids": permission_ids
    }


@router.get("/roles/{role_id}/all-permissions")
async def get_role_all_permissions(
    role_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取角色的所有权限（包括继承的权限）"""
    role = await db.execute(
        select(Role).where(Role.id == role_id)
    )
    role = role.scalar()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    # 获取角色的所有权限（包括继承的）
    permissions = await PermissionService.get_role_permissions(db, role_id)
    
    permission_list = []
    for perm in permissions:
        permission_list.append({
            "id": perm.id,
            "permission_name": perm.permission_name,
            "permission_code": perm.permission_code,
            "parent_id": perm.parent_id,
            "type": perm.type,
            "path": perm.path,
            "component": perm.component,
            "icon": perm.icon,
            "sort": perm.sort,
            "status": perm.status
        })
    
    return {
        "items": permission_list,
        "total": len(permission_list)
    }
