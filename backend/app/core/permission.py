from typing import Optional, List, Tuple
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.services.class_assistant_service import ClassAssistantService


class PermissionChecker:
    """权限检查工具类"""
    
    # 角色名称常量
    TEACHER_ROLES = ["super_admin", "admin", "teacher"]
    ADMIN_ROLES = ["super_admin", "admin"]
    
    @staticmethod
    def is_teacher(user: User) -> bool:
        """检查用户是否是导师角色"""
        return user.role.role_name in PermissionChecker.TEACHER_ROLES
    
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
        
        返回: (is_teacher, is_assistant, assistant_class_ids)
        """
        is_teacher = PermissionChecker.is_teacher(user)
        
        # 如果是导师，直接返回
        if is_teacher:
            return True, False, None
        
        # 检查是否是班级助理
        is_assistant = False
        assistant_class_ids = None
        
        if class_id:
            # 检查是否是指定班级的助理
            is_assistant = await ClassAssistantService.is_assistant_of_class(db, user.id, class_id)
        else:
            # 获取所有授权班级
            assistant_classes = await ClassAssistantService.get_user_assistant_classes(db, user.id)
            if assistant_classes:
                is_assistant = True
                assistant_class_ids = [cls.id for cls in assistant_classes]
        
        return is_teacher, is_assistant, assistant_class_ids
    
    @staticmethod
    async def require_growth_permission(
        db: AsyncSession,
        user: User,
        class_id: Optional[int] = None
    ) -> Tuple[bool, Optional[List[int]]]:
        """
        要求成长值操作权限
        
        如果用户没有权限，抛出HTTPException
        
        返回: (is_teacher, assistant_class_ids)
        """
        is_teacher, is_assistant, assistant_class_ids = await PermissionChecker.check_growth_permission(
            db, user, class_id
        )
        
        # 如果用户是班级助理，直接返回，不检查是否是学员
        if is_assistant:
            return False, assistant_class_ids
        
        # 检查用户是否是学员
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
        is_student = student_class_result.scalar_one_or_none() is not None
        
        if not (is_teacher or is_student):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限操作成长值"
            )
        
        return is_teacher, assistant_class_ids