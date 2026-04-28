from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.user import Role, User
from app.models.permission import Permission, RolePermission
from app.core.logger import logger


class PermissionService:
    @staticmethod
    async def get_role_permissions(
        db: AsyncSession,
        role_id: int
    ) -> List[Permission]:
        """获取角色的所有权限（包括继承的权限）"""
        # 获取角色信息
        role = await db.get(Role, role_id)
        if not role:
            return []
        
        # 收集所有父角色ID
        role_ids = [role_id]
        current_role = role
        while current_role.parent_id:
            current_role = await db.get(Role, current_role.parent_id)
            if current_role:
                role_ids.append(current_role.id)
            else:
                break
        
        # 查询所有角色的权限
        query = select(Permission).join(RolePermission).where(
            RolePermission.role_id.in_(role_ids)
        )
        result = await db.execute(query)
        permissions = result.scalars().all()
        
        # 去重
        permission_set = set()
        unique_permissions = []
        for perm in permissions:
            if perm.id not in permission_set:
                permission_set.add(perm.id)
                unique_permissions.append(perm)
        
        return unique_permissions
    
    @staticmethod
    async def check_user_permission(
        db: AsyncSession,
        user_id: int,
        permission_code: str
    ) -> bool:
        """检查用户是否有指定权限"""
        # 获取用户信息
        user = await db.get(User, user_id)
        if not user:
            return False
        
        # 获取角色的所有权限
        permissions = await PermissionService.get_role_permissions(db, user.role_id)
        
        # 检查是否有指定权限
        for perm in permissions:
            if perm.permission_code == permission_code:
                return True
        
        return False
    
    @staticmethod
    async def create_permission_template(
        db: AsyncSession,
        role_id: int,
        template_name: str,
        permission_codes: List[str]
    ) -> Dict[str, Any]:
        """创建权限模板"""
        # 获取角色信息
        role = await db.get(Role, role_id)
        if not role:
            raise ValueError("角色不存在")
        
        # 清除角色现有的权限
        await db.execute(
            RolePermission.__table__.delete().where(
                RolePermission.role_id == role_id
            )
        )
        
        # 添加新权限
        for code in permission_codes:
            # 查找权限
            perm_result = await db.execute(
                select(Permission).where(Permission.permission_code == code)
            )
            perm = perm_result.scalar_one_or_none()
            if perm:
                role_permission = RolePermission(
                    role_id=role_id,
                    permission_id=perm.id
                )
                db.add(role_permission)
        
        await db.commit()
        logger.info(f"创建权限模板: template_name={template_name}, role_id={role_id}, permissions={len(permission_codes)}")
        
        return {
            "message": "权限模板创建成功",
            "role_id": role_id,
            "template_name": template_name,
            "permission_count": len(permission_codes)
        }
    
    @staticmethod
    async def get_permission_tree(
        db: AsyncSession
    ) -> List[Dict[str, Any]]:
        """获取权限树结构"""
        # 获取所有权限
        result = await db.execute(select(Permission))
        permissions = result.scalars().all()
        
        # 构建权限树
        permission_map = {}
        root_permissions = []
        
        for perm in permissions:
            permission_map[perm.id] = {
                "id": perm.id,
                "permission_name": perm.permission_name,
                "permission_code": perm.permission_code,
                "parent_id": perm.parent_id,
                "type": perm.type,
                "path": perm.path,
                "component": perm.component,
                "icon": perm.icon,
                "sort": perm.sort,
                "status": perm.status,
                "children": []
            }
        
        for perm_id, perm_data in permission_map.items():
            parent_id = perm_data["parent_id"]
            if parent_id is None:
                root_permissions.append(perm_data)
            elif parent_id in permission_map:
                permission_map[parent_id]["children"].append(perm_data)
        
        # 按排序字段排序
        def sort_permissions(perms):
            perms.sort(key=lambda x: x["sort"])
            for perm in perms:
                if perm["children"]:
                    sort_permissions(perm["children"])
        
        sort_permissions(root_permissions)
        
        return root_permissions