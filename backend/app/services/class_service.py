import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.class_info import ClassInfo
from app.models.class_student import ClassStudent
from app.models.growth_log import Growth
from app.schemas.class_info import ClassCreate, ClassUpdate, ClassStatusUpdate
from app.core.logger import logger


class ClassService:
    """班级服务"""
    
    @staticmethod
    async def get_class_by_id(db: AsyncSession, class_id: int) -> Optional[ClassInfo]:
        """根据ID获取班级"""
        from sqlalchemy.orm import selectinload
        result = await db.execute(
            select(ClassInfo)
            .options(selectinload(ClassInfo.teacher))
            .where(ClassInfo.id == class_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_class_by_qr_code(db: AsyncSession, qr_code: str) -> Optional[ClassInfo]:
        """根据二维码获取班级"""
        from sqlalchemy.orm import selectinload
        result = await db.execute(
            select(ClassInfo)
            .options(selectinload(ClassInfo.teacher))
            .where(ClassInfo.qr_code == qr_code)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_class(db: AsyncSession, class_data: ClassCreate, teacher_id: int) -> ClassInfo:
        """创建班级"""
        # 生成唯一二维码标识
        qr_code = str(uuid.uuid4()).replace("-", "")
        
        # 生成二维码数据
        qr_data = f"class:{qr_code}"
        
        db_class = ClassInfo(
            school_name=class_data.school_name,
            session=class_data.session,
            class_name=class_data.class_name,
            description=class_data.description,
            teacher_id=teacher_id,
            qr_code=qr_code,
            qr_url=qr_data,
            status=True
        )
        
        db.add(db_class)
        await db.commit()
        await db.refresh(db_class)
        
        logger.info(f"班级创建成功: {db_class.id}, 导师: {teacher_id}")
        return db_class
    
    @staticmethod
    async def update_class(db: AsyncSession, class_info: ClassInfo, class_data: ClassUpdate) -> ClassInfo:
        """更新班级"""
        if class_data.class_name:
            class_info.class_name = class_data.class_name
        if class_data.session:
            class_info.session = class_data.session
        
        await db.commit()
        await db.refresh(class_info)
        
        logger.info(f"班级更新: {class_info.id}")
        return class_info
    
    @staticmethod
    async def update_class_status(db: AsyncSession, class_info: ClassInfo, status_update: ClassStatusUpdate) -> ClassInfo:
        """更新班级状态"""
        # 如果要关闭班级，检查是否有未处理的兑换记录，并停用所有学员
        if not status_update.status and class_info.status:
            # 检查是否有待核销的订单
            from app.models.gift_order import GiftOrder
            result = await db.execute(
                select(func.count(GiftOrder.id)).where(
                    GiftOrder.class_id == class_info.id,
                    GiftOrder.status == 0  # 待核销
                )
            )
            pending_count = result.scalar()

            if pending_count > 0:
                raise ValueError(f"班级还有{pending_count}个待核销订单，无法关闭")

            # 停用班级下所有学员
            from app.models.class_student import ClassStudent, BindStatus
            active_students = await db.execute(
                select(ClassStudent).where(
                    ClassStudent.class_id == class_info.id,
                    ClassStudent.bind_status == BindStatus.APPROVED,
                    ClassStudent.is_active == True,
                    ClassStudent.is_deleted == False
                )
            )
            students_to_deactivate = active_students.scalars().all()
            for student in students_to_deactivate:
                student.is_active = False

        class_info.status = status_update.status
        await db.commit()
        await db.refresh(class_info)

        # 清除相关缓存
        from app.core.cache import cache
        cache_pattern = f"students:teacher:{class_info.teacher_id}:*"
        await cache.clear_pattern(cache_pattern)

        status_text = "开放" if class_info.status else "关闭"
        logger.info(f"班级状态更新: {class_info.id}, 状态: {status_text}")
        return class_info
    
    @staticmethod
    async def get_teacher_classes(
        db: AsyncSession,
        teacher_id: int,
        status: Optional[bool] = None
    ) -> List[ClassInfo]:
        """获取导师的班级列表"""
        query = select(ClassInfo).where(ClassInfo.teacher_id == teacher_id)
        
        if status is not None:
            query = query.where(ClassInfo.status == status)
        
        query = query.order_by(ClassInfo.created_at.desc())
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_all_classes(
        db: AsyncSession,
        school_name: Optional[str] = None,
        session: Optional[str] = None,
        status: Optional[bool] = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[ClassInfo], int]:
        """获取所有班级（管理员用）"""
        base_query = select(ClassInfo)
        
        if school_name:
            base_query = base_query.where(ClassInfo.school_name.contains(school_name))
        
        if session:
            base_query = base_query.where(ClassInfo.session.contains(session))
        
        if status is not None:
            base_query = base_query.where(ClassInfo.status == status)
        
        # 获取总数
        count_query = select(func.count()).select_from(base_query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        # 获取分页数据
        query = base_query.offset(skip).limit(limit).order_by(ClassInfo.created_at.desc())
        result = await db.execute(query)
        classes = result.scalars().all()
        
        return classes, total
    
    @staticmethod
    async def get_class_student_count(db: AsyncSession, class_id: int) -> int:
        """获取班级学员数量（只统计ClassStudent表）"""
        # 统计ClassStudent表中的学员数量，计算已通过或未绑定（导师导入）且未删除且未停用的学员
        from app.models.class_student import BindStatus
        class_student_result = await db.execute(
            select(func.count(ClassStudent.id)).where(
                ClassStudent.class_id == class_id,
                ClassStudent.bind_status.in_([BindStatus.NONE.value, BindStatus.APPROVED.value]),
                ClassStudent.is_deleted == False,
                ClassStudent.is_active == True
            )
        )
        class_student_count = class_student_result.scalar()

        return class_student_count or 0
