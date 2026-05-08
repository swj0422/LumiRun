from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.permission import Permission, RolePermission

router = APIRouter()


@router.get("/menus")
async def get_user_menus(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """鑾峰彇褰撳墠鐢ㄦ埛鐨勮彍鍗曟潈闄?""
    result = await db.execute(
        select(Permission)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .where(RolePermission.role_id == current_user.role_id)
        .where(Permission.type == 1)
        .where(Permission.status == True)
        .order_by(Permission.sort)
    )
    permissions = result.scalars().all()
    
    menus = []
    for perm in permissions:
        menus.append({
            "id": perm.id,
            "name": perm.permission_name,
            "code": perm.permission_code,
            "path": perm.path,
            "component": perm.component,
            "icon": perm.icon,
            "sort": perm.sort
        })
    
    return menus


@router.get("/permissions")
async def get_user_permissions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """鑾峰彇褰撳墠鐢ㄦ埛鐨勬墍鏈夋潈闄愮爜"""
    result = await db.execute(
        select(Permission.permission_code)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .where(RolePermission.role_id == current_user.role_id)
        .where(Permission.status == True)
    )
    permission_codes = [row[0] for row in result.all()]
    
    return {"permissions": permission_codes}
