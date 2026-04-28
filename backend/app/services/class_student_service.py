from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from app.models.class_student import ClassStudent, BindStatus
from app.models.class_info import ClassInfo
from app.models.user import User
from app.core.logger import logger
from datetime import datetime


class ClassStudentService:
    @staticmethod
    async def add_student(
        db: AsyncSession,
        class_id: int,
        student_no_in_class: str,
        name_in_class: str
    ) -> ClassStudent:
        existing_student = await ClassStudentService.get_student_by_class_and_no(db, class_id, student_no_in_class)
        if existing_student:
            raise ValueError(f"学号 {student_no_in_class} 在该班级中已存在")
        
        student = ClassStudent(
            class_id=class_id,
            student_no_in_class=student_no_in_class,
            name_in_class=name_in_class,
            bind_status=BindStatus.APPROVED
        )
        db.add(student)
        await db.commit()
        await db.refresh(student)
        logger.info(f"添加学员到班级: class_id={class_id}, student_no_in_class={student_no_in_class}, name_in_class={name_in_class}")
        return student

    @staticmethod
    async def batch_add_students(
        db: AsyncSession,
        class_id: int,
        students: List[dict]
    ) -> List[ClassStudent]:
        result = []
        seen_student_nos = set()
        
        for student_data in students:
            student_no_in_class = student_data.get("student_no_in_class")
            if not student_no_in_class:
                raise ValueError(f"学员 {student_data.get('name_in_class', '未知')} 缺少学号")
            
            # 检查批量数据中是否有重复学号
            if student_no_in_class in seen_student_nos:
                raise ValueError(f"学号 {student_no_in_class} 在导入数据中重复")
            seen_student_nos.add(student_no_in_class)
            
            # 检查学号是否在班级中已存在
            existing_student = await ClassStudentService.get_student_by_class_and_no(db, class_id, student_no_in_class)
            if existing_student:
                raise ValueError(f"学号 {student_no_in_class} 在该班级中已存在")
            
            student = ClassStudent(
                class_id=class_id,
                student_no_in_class=student_no_in_class,
                name_in_class=student_data["name_in_class"],
                bind_status=BindStatus.APPROVED
            )
            db.add(student)
            result.append(student)
        await db.commit()
        logger.info(f"批量添加学员到班级: class_id={class_id}, count={len(students)}")
        return result

    @staticmethod
    async def get_students_by_class(
        db: AsyncSession,
        class_id: int,
        status: Optional[str] = None
    ) -> List[ClassStudent]:
        query = select(ClassStudent).where(
            ClassStudent.class_id == class_id,
            ClassStudent.is_deleted == False
        )
        if status is not None:
            # 将字符串状态转换为枚举值
            status_enum = getattr(BindStatus, status.upper(), None)
            if status_enum:
                query = query.where(ClassStudent.bind_status == status_enum)
        query = query.order_by(ClassStudent.student_no_in_class, ClassStudent.name_in_class)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_student_by_id(db: AsyncSession, student_id: int) -> Optional[ClassStudent]:
        from sqlalchemy.orm import joinedload
        result = await db.execute(
            select(ClassStudent).options(
                joinedload(ClassStudent.class_info)
            ).where(ClassStudent.id == student_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def update_student(
        db: AsyncSession,
        student_id: int,
        student_no_in_class: Optional[str],
        name_in_class: str
    ) -> Optional[ClassStudent]:
        student = await ClassStudentService.get_student_by_id(db, student_id)
        if not student:
            return None
        student.student_no_in_class = student_no_in_class
        student.name_in_class = name_in_class
        await db.commit()
        await db.refresh(student)
        logger.info(f"更新学员信息: student_id={student_id}")
        return student

    @staticmethod
    async def delete_student(db: AsyncSession, student_id: int) -> bool:
        student = await ClassStudentService.get_student_by_id(db, student_id)
        if not student:
            return False
        # 标记为已删除，保留所有历史数据
        from datetime import datetime
        student.is_deleted = True
        student.deleted_at = datetime.now()
        await db.commit()
        logger.info(f"标记删除学员: student_id={student_id}")
        return True

    @staticmethod
    async def bind_student(
        db: AsyncSession,
        student_id: int,
        user_id: int
    ) -> Optional[ClassStudent]:
        student = await ClassStudentService.get_student_by_id(db, student_id)
        if not student:
            return None
        student.student_profile_id = user_id
        student.bind_status = BindStatus.PENDING
        student.bind_time = datetime.now()
        await db.commit()
        await db.refresh(student)
        logger.info(f"绑定申请: student_id={student_id}, user_id={user_id}")
        return student

    @staticmethod
    async def approve_bind(
        db: AsyncSession,
        student_id: int
    ) -> Optional[ClassStudent]:
        student = await ClassStudentService.get_student_by_id(db, student_id)
        if not student:
            return None
        student.bind_status = BindStatus.APPROVED
        await db.commit()
        await db.refresh(student)
        logger.info(f"同意绑定: student_id={student_id}")
        return student

    @staticmethod
    async def reject_bind(
        db: AsyncSession,
        student_id: int
    ) -> Optional[ClassStudent]:
        student = await ClassStudentService.get_student_by_id(db, student_id)
        if not student:
            return None
        student.bind_status = BindStatus.REJECTED
        await db.commit()
        await db.refresh(student)
        logger.info(f"拒绝绑定: student_id={student_id}")
        return student

    @staticmethod
    async def find_students_by_name(
        db: AsyncSession,
        class_id: int,
        name_in_class: str,
        include_unbound: bool = True
    ) -> List[ClassStudent]:
        """根据班级ID和姓名查找学员，支持查找未绑定或已解绑的学员"""
        # 去除空格，转换为小写进行模糊匹配
        search_name = name_in_class.strip().lower()
        
        query = select(ClassStudent).where(
            and_(
                ClassStudent.class_id == class_id,
                or_(
                    func.lower(ClassStudent.name_in_class) == search_name,  # 精确匹配
                    func.lower(ClassStudent.name_in_class).like(f'%{search_name}%')  # 模糊匹配
                ),
                ClassStudent.is_deleted == False
            )
        )
        
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_student_count(db: AsyncSession, class_id: int) -> int:
        from app.models.class_student import BindStatus
        result = await db.execute(
            select(func.count(ClassStudent.id)).where(
                ClassStudent.class_id == class_id,
                ClassStudent.bind_status == BindStatus.APPROVED,
                ClassStudent.is_deleted == False,
                ClassStudent.is_active == True
            )
        )
        return result.scalar() or 0

    @staticmethod
    async def get_student_by_class_and_no(
        db: AsyncSession,
        class_id: int,
        student_no_in_class: str
    ) -> Optional[ClassStudent]:
        result = await db.execute(
            select(ClassStudent).where(
                and_(
                    ClassStudent.class_id == class_id,
                    ClassStudent.student_no_in_class == student_no_in_class,
                    ClassStudent.is_deleted == False
                )
            )
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def switch_class(
        db: AsyncSession,
        student_id: int,
        new_class_id: int
    ) -> Optional[ClassStudent]:
        """学员切换班级"""
        # 获取学员信息
        student = await ClassStudentService.get_student_by_id(db, student_id)
        if not student:
            return None
        
        # 获取新班级信息
        from app.models.class_info import ClassInfo
        new_class = await db.get(ClassInfo, new_class_id)
        if not new_class:
            raise ValueError("新班级不存在")
        
        # 将该学员在所有班级的is_current设置为False
        from sqlalchemy import update
        await db.execute(
            update(ClassStudent)
            .where(ClassStudent.student_profile_id == student.student_profile_id)
            .values(is_current=False)
        )
        
        # 创建新的班级学员记录
        new_student = ClassStudent(
            class_id=new_class_id,
            student_profile_id=student.student_profile_id,
            name_in_class=student.name_in_class,
            student_no_in_class=student.student_no_in_class,
            bind_status=BindStatus.APPROVED,
            is_current=True,
            bind_time=datetime.utcnow()
        )
        db.add(new_student)
        
        await db.commit()
        await db.refresh(new_student)
        logger.info(f"学员切换班级: student_id={student_id}, old_class_id={student.class_id}, new_class_id={new_class_id}")
        return new_student
