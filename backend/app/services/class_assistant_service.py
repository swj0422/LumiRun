from typing import Optional, List
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.models.class_assistant import ClassAssistant
from app.models.user import User
from app.models.class_info import ClassInfo
from app.models.class_student import ClassStudent
from app.models.student_profile import StudentProfile
from app.core.logger import logger


class ClassAssistantService:
    """班级助理服务"""


    @staticmethod
    async def add_assistant(
        db: AsyncSession,
        teacher_id: int,
        class_id: int,
        assistant_id: int,
        assistant_email: str
    ) -> ClassAssistant:
        """添加班级助理"""
        # 检查班级是否存在且属于该导师
        class_info = await db.execute(
            select(ClassInfo).where(
                and_(
                    ClassInfo.id == class_id,
                    ClassInfo.teacher_id == teacher_id
                )
            )
        )
        class_info = class_info.scalar_one_or_none()

        if not class_info:
            raise ValueError("班级不存在或无权限")

        # 检查助理用户是否存在，支持学员ID和邮箱
        user_id = None

        # 尝试从学员表中查找用户ID（适用于从学员列表选择的情况）
        student = await db.execute(
            select(ClassStudent).where(ClassStudent.id == assistant_id)
        )
        student = student.scalar_one_or_none()

        if student:
            # 如果是学员，检查是否已绑定
            if not student.student_profile_id:
                raise ValueError("非注册学员，不能添加为助理")
            # 从学员档案中获取用户ID
            student_profile = await db.execute(
                select(StudentProfile).where(StudentProfile.id == student.student_profile_id)
            )
            student_profile = student_profile.scalar_one_or_none()
            if not student_profile:
                raise ValueError("学员档案不存在")
            user_id = student_profile.user_id
        else:
            # 如果不是学员ID，则根据邮箱查找用户（适用于输入邮箱的情况）
            user_by_email = await db.execute(
                select(User).where(User.email == assistant_email)
            )
            user_by_email = user_by_email.scalar_one_or_none()
            if user_by_email:
                user_id = user_by_email.id

        # 如果仍然没有找到用户ID，返回错误
        if user_id is None:
            raise ValueError("用户不存在")

        # 检查用户是否存在
        assistant = await db.execute(
            select(User).where(User.id == user_id)
        )
        assistant = assistant.scalar_one_or_none()

        if not assistant:
            raise ValueError("用户不存在")

        # 创建班级助理
        try:
            class_assistant = ClassAssistant(
                teacher_id=teacher_id,
                class_id=class_id,
                assistant_id=user_id,
                assistant_email=assistant_email,
                status=True
            )
            db.add(class_assistant)
            await db.commit()
            await db.refresh(class_assistant)

            logger.info(f"添加班级助理成功: 班级ID={class_id}, 助理ID={user_id}, 导师ID={teacher_id}")
            return class_assistant
        except IntegrityError:
            await db.rollback()
            raise ValueError("该用户已经是该班级的助理")

    @staticmethod
    async def remove_assistant(
        db: AsyncSession,
        teacher_id: int,
        class_id: int,
        assistant_id: int
    ) -> bool:
        """移除班级助理"""
        # 检查班级是否存在且属于该导师
        class_info = await db.execute(
            select(ClassInfo).where(
                and_(
                    ClassInfo.id == class_id,
                    ClassInfo.teacher_id == teacher_id
                )
            )
        )
        class_info = class_info.scalar_one_or_none()

        if not class_info:
            raise ValueError("班级不存在或无权限")

        # 查找并删除班级助理
        class_assistant = await db.execute(
            select(ClassAssistant).where(
                and_(
                    ClassAssistant.class_id == class_id,
                    ClassAssistant.assistant_id == assistant_id
                )
            )
        )
        class_assistant = class_assistant.scalar_one_or_none()

        if not class_assistant:
            raise ValueError("该用户不是该班级的助理")

        await db.delete(class_assistant)
        await db.commit()

        logger.info(f"移除班级助理成功: 班级ID={class_id}, 助理ID={assistant_id}, 导师ID={teacher_id}")
        return True

    @staticmethod
    async def get_class_assistants(
        db: AsyncSession,
        class_id: int
    ) -> List[ClassAssistant]:
        """获取班级的助理列表"""
        result = await db.execute(
            select(ClassAssistant).where(
                ClassAssistant.class_id == class_id
            ).order_by(ClassAssistant.created_at.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def get_user_assistant_classes(
        db: AsyncSession,
        assistant_id: int
    ) -> List[ClassInfo]:
        """获取用户作为助理的班级列表"""
        result = await db.execute(
            select(ClassInfo).join(
                ClassAssistant,
                and_(
                    ClassAssistant.class_id == ClassInfo.id,
                    ClassAssistant.assistant_id == assistant_id,
                    ClassAssistant.status == True
                )
            ).order_by(ClassInfo.created_at.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def is_assistant_of_class(
        db: AsyncSession,
        assistant_id: int,
        class_id: int
    ) -> bool:
        """检查用户是否是班级的助理"""
        result = await db.execute(
            select(ClassAssistant).where(
                and_(
                    ClassAssistant.assistant_id == assistant_id,
                    ClassAssistant.class_id == class_id,
                    ClassAssistant.status == True
                )
            )
        )
        return result.scalar_one_or_none() is not None