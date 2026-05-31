from typing import Optional, List, Tuple
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.services.class_assistant_service import ClassAssistantService


class PermissionChecker:
    """权限检查工具类"""

    MANAGER_ROLES = ["super_admin", "admin", "manager"]
    ADMIN_ROLES = ["super_admin", "admin"]

    @staticmethod
    def is_manager(user: User) -> bool:
        """检查用户是否是管理者角色"""
        return user.role.role_name in PermissionChecker.MANAGER_ROLES
    
    @staticmethod
    def is_admin(user: User) -> bool:
        """检查用户是否是管理员角色"""
        return user.role.role_name in PermissionChecker.ADMIN_ROLES
    
    @staticmethod
    async def check_growth_permission(
        db: AsyncSession,
        user: User,
        class_id: Optional[int] = None
    ) -> Tuple[bool, bool, Optional[List[int]]]:
        """
        检查成长值相关权限

        返回: (is_manager, is_assistant, assistant_class_ids)
        """
        is_manager = PermissionChecker.is_manager(user)

        if is_manager:
            return True, False, None

        is_assistant = False
        assistant_class_ids = None

        if class_id:
            is_assistant = await ClassAssistantService.is_assistant_of_class(db, user.id, class_id)
        else:
            assistant_classes = await ClassAssistantService.get_user_assistant_classes(db, user.id)
            if assistant_classes:
                is_assistant = True
                assistant_class_ids = [cls.id for cls in assistant_classes]

        return is_manager, is_assistant, assistant_class_ids

    @staticmethod
    async def require_growth_permission(
        db: AsyncSession,
        user: User,
        class_id: Optional[int] = None
    ) -> Tuple[bool, Optional[List[int]]]:
        """
        要求成长值操作权限

        如果用户没有权限，抛出HTTPException

        返回: (is_manager, assistant_class_ids)
        """
        is_manager, is_assistant, assistant_class_ids = await PermissionChecker.check_growth_permission(
            db, user, class_id
        )

        if is_assistant:
            return False, assistant_class_ids

        from app.models.student_profile import StudentProfile
        from app.models.class_student import ClassStudent
        from sqlalchemy import select

        student_class_result = await db.execute(
            select(ClassStudent.id).join(
                StudentProfile, StudentProfile.id == ClassStudent.student_profile_id
            ).where(
                StudentProfile.user_id == user.id
            )
        )
        is_member = student_class_result.scalar_one_or_none() is not None

        if not (is_manager or is_member):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限操作成长值"
            )

        return is_manager, assistant_class_ids