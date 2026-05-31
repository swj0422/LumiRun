from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_user, require_teacher
from app.schemas.student_class import StudentBind, StudentClassResponse, StudentSimpleResponse
from app.services.student_service import StudentService
from app.services.student_operation_log_service import StudentOperationLogService
from app.services.student_log_helper import log_system_operation, log_student_operation
from app.models.user import User
from app.models.class_info import ClassInfo
from app.models.class_student import BindStatus
from pydantic import BaseModel
from app.core.cache import cache
from app.services.log_service import LogService
from app.models.system_log import LogType, LogLevel
from app.core.logger import logger

router = APIRouter()


class StudentCreate(BaseModel):
    class_id: int
    student_no: str
    real_name: str


class StudentNoteCreate(BaseModel):
    real_name: Optional[str] = None
    learning_characteristics: Optional[str] = None
    personality_suggestions: Optional[str] = None
    performance_summary: Optional[str] = None
    tags: Optional[str] = None


@router.post("/bind", response_model=dict)
async def bind_class(
    bind_data: StudentBind,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """学员绑定班级"""
    try:
        # 检查用户是否是学员
        if current_user.role.role_name != "student":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有学员可以绑定班级"
            )

        # 获取班级信息
        from sqlalchemy import select
        from app.models.class_info import ClassInfo
        from app.services.class_student_service import ClassStudentService

        # qr_code 可能是班级ID（数字）或班级二维码内容（如 class_001）
        qr_code = bind_data.qr_code.strip()
        class_id = None
        try:
            class_id = int(qr_code)
            result = await db.execute(select(ClassInfo).where(ClassInfo.id == class_id))
            class_info = result.scalar_one_or_none()
        except ValueError:
            result = await db.execute(select(ClassInfo).where(ClassInfo.qr_code == qr_code))
            class_info = result.scalar_one_or_none()
            if class_info:
                class_id = class_info.id

        if not class_info or not class_id:
            raise ValueError("班级不存在或无效的班级二维码")

        # 查找对应的学员记录（bind_status 为 NONE 或 UNBOUND）
        students = await ClassStudentService.find_students_by_name(
            db, class_id, bind_data.name_in_class, include_unbound=True
        )

        if not students:
            raise ValueError("未找到对应的学员，请核对班级、姓名和学号")

        # 找到匹配的学员（优先匹配学号）
        student = None
        for s in students:
            if s.student_no_in_class == bind_data.student_no_in_class:
                student = s
                break

        # 如果没有精确匹配学号，使用第一个（理论上应该只有一个）
        if not student:
            student = students[0] if students else None

        if not student:
            raise ValueError("未找到对应的学员，请核对班级、姓名和学号")

        # 检查学员是否已经绑定了其他用户
        # 注意：student_profile_id 引用的是 student_profile.id，不是 sys_user.id
        from app.models.student_profile import StudentProfile
        student_profile_result = await db.execute(
            select(StudentProfile).where(StudentProfile.user_id == current_user.id)
        )
        student_profile = student_profile_result.scalar_one_or_none()

        if not student_profile:
            raise ValueError("学员档案不存在，请先创建学员档案")

        if student.student_profile_id and student.student_profile_id != student_profile.id:
            raise ValueError("该学员已经绑定了其他账号")

        # 更新学员信息（保存学员输入的姓名和学号）
        student.name_in_class = bind_data.name_in_class
        student.student_no_in_class = bind_data.student_no_in_class
        student.student_profile_id = student_profile.id
        student.bind_status = BindStatus.PENDING
        student.bind_time = datetime.now()

        await db.commit()
        await db.refresh(student)

        return {
            "message": "绑定申请已提交，请等待导师审核",
            "student_class_id": student.id,
            "class_name": class_info.class_name
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/bind/approve/{student_class_id}", response_model=dict)
async def approve_bind(
    request: Request,
    student_class_id: int,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    """同意绑定申请"""
    try:
        from app.services.class_student_service import ClassStudentService
        
        # 获取学员信息
        student = await ClassStudentService.get_student_by_id(db, student_class_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="学员不存在"
            )
        
        # 检查是否是该班级的导师
        class_info = student.class_info
        if not class_info or class_info.teacher_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限操作此学员"
            )
        
        # 检查绑定状态是否为待审核
        if student.bind_status != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该学员绑定状态不是待审核"
            )
        
        # 同意绑定
        approved_student = await ClassStudentService.approve_bind(db, student_class_id)
        
        # 记录学员操作日志
        from app.services.student_operation_log_service import StudentOperationLogService
        await StudentOperationLogService.create_operation_log(
            operator_id=current_user.id,
            operator_name=current_user.real_name or current_user.username,
            class_id=student.class_id,
            class_student_id=student.id,
            class_name=class_info.class_name,
            student_name=student.name_in_class,
            operation_type="approve_bind",
            operation_content=f"同意绑定申请：{student.name_in_class}",
            before_data={"bind_status": student.bind_status.value},
            after_data={"bind_status": approved_student.bind_status.value},
            ip_address=request.client.host if request.client else None
        )
        
        # 发送绑定成功通知给学员
        if student.student_profile_id:
            from app.services.message_service import MessageService
            from app.models.user import User
            from sqlalchemy import select
            # 获取学员用户信息
            user_result = await db.execute(
                select(User).where(User.id == student.student_profile_id)
            )
            student_user = user_result.scalar_one_or_none()
            if student_user:
                await MessageService.create_message(
                    db=db,
                    user_id=student_user.id,
                    content=f"您申请绑定 {class_info.class_name} 班级的申请已被同意，现在可以查看班级信息了。",
                    message_type=3  # 成长值变动通知类型，或使用合适的类型
                )
        
        return {
            "message": "绑定申请已同意"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/bind/pending", response_model=List[dict])
async def get_pending_binds(
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    """获取当前导师班级的待审核绑定申请"""
    try:
        from sqlalchemy import select, and_
        from app.models.class_student import ClassStudent, BindStatus
        from app.models.class_info import ClassInfo

        # 获取当前导师的所有班级
        result = await db.execute(
            select(ClassInfo).where(ClassInfo.teacher_id == current_user.id)
        )
        classes = result.scalars().all()
        class_ids = [cls.id for cls in classes]

        if not class_ids:
            return []

        # 获取这些班级的待审核绑定申请
        result = await db.execute(
            select(ClassStudent, ClassInfo).join(
                ClassInfo, ClassStudent.class_id == ClassInfo.id
            ).where(
                and_(
                    ClassStudent.class_id.in_(class_ids),
                    ClassStudent.bind_status == BindStatus.PENDING,
                    ClassStudent.is_deleted == False
                )
            )
        )
        pending_binds = result.all()

        return [
            {
                "student_class_id": student.id,
                "class_id": student.class_id,
                "class_name": class_info.class_name,
                "student_name": student.name_in_class,
                "student_no": student.student_no_in_class,
                "bind_time": student.bind_time.isoformat() if student.bind_time else None
            }
            for student, class_info in pending_binds
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/bind/reject/{student_class_id}", response_model=dict)
async def reject_bind(
    request: Request,
    student_class_id: int,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    """拒绝绑定申请"""
    try:
        from app.services.class_student_service import ClassStudentService
        
        # 获取学员信息
        student = await ClassStudentService.get_student_by_id(db, student_class_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="学员不存在"
            )
        
        # 检查是否是该班级的导师
        class_info = student.class_info
        if not class_info or class_info.teacher_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限操作此学员"
            )
        
        # 检查绑定状态是否为待审核
        if student.bind_status != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该学员绑定状态不是待审核"
            )
        
        # 拒绝绑定
        rejected_student = await ClassStudentService.reject_bind(db, student_class_id)
        
        # 记录学员操作日志
        from app.services.student_operation_log_service import StudentOperationLogService
        await StudentOperationLogService.create_operation_log(
            operator_id=current_user.id,
            operator_name=current_user.real_name or current_user.username,
            class_id=student.class_id,
            class_student_id=student.id,
            class_name=class_info.class_name,
            student_name=student.name_in_class,
            operation_type="reject_bind",
            operation_content=f"拒绝绑定申请：{student.name_in_class}",
            before_data={"bind_status": student.bind_status.value},
            after_data={"bind_status": rejected_student.bind_status.value},
            ip_address=request.client.host if request.client else None
        )
        
        return {
            "message": "绑定申请已拒绝"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/", response_model=dict)
async def add_student(
    request: Request,
    student_data: StudentCreate,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    """添加学员"""
    try:
        result = await StudentService.add_student(
            db,
            student_data.class_id,
            student_data.student_no,
            student_data.real_name,
            current_user.id
        )
        
        # 记录系统操作日志
        await log_system_operation(
            db=db,
            request=request,
            user_id=current_user.id,
            action="添加学员",
            biz_id=result['student_info']['id'],
            request_params={
                "class_id": student_data.class_id,
                "student_no": student_data.student_no,
                "real_name": student_data.real_name
            }
        )
        
        # 记录学员操作日志
        if result and 'student_info' in result:
            student_info = result['student_info']
            from sqlalchemy import select
            from app.models.class_info import ClassInfo
            class_result = await db.execute(select(ClassInfo).where(ClassInfo.id == student_info['class_id']))
            class_info = class_result.scalar_one_or_none()
            class_name = class_info.class_name if class_info else "未知班级"
            
            await StudentOperationLogService.create_operation_log(
                operator_id=current_user.id,
                operator_name=current_user.real_name or current_user.username,
                class_id=student_info['class_id'],
                class_student_id=student_info['id'],
                class_name=class_name,
                student_name=student_info['name_in_class'],
                operation_type="add",
                operation_content=f"添加学员：{student_info['name_in_class']}（学号：{student_info['student_no_in_class']}）",
                before_data=None,
                after_data=student_info,
                ip_address=request.client.host if request.client else None
            )
        
        return {
            "message": result["message"],
            **({"student_id": result["student_info"]["id"]} if result["status"] == "added" else {})
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )






@router.get("/my-classes", response_model=List[dict])
async def get_my_classes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取我的绑定班级"""
    # 查找用户的学员档案
    from app.models.student_profile import StudentProfile
    from sqlalchemy import select

    student_profile = await db.execute(
        select(StudentProfile).where(StudentProfile.user_id == current_user.id)
    )
    student_profile = student_profile.scalar_one_or_none()

    if not student_profile:
        return []
    
    # 查找该学员档案的所有绑定班级
    from app.models.class_student import ClassStudent
    from sqlalchemy.orm import selectinload
    
    bindings = await db.execute(
        select(ClassStudent).options(
            selectinload(ClassStudent.class_info).options(
                selectinload(ClassInfo.teacher)
            )
        ).where(
            ClassStudent.student_profile_id == student_profile.id,
            ClassStudent.bind_status == BindStatus.APPROVED
        )
    )
    bindings = bindings.scalars().all()
    
    classes = []
    for binding in bindings:
        classes.append({
            "id": binding.id,
            "class_id": binding.class_id,
            "class_name": binding.class_info.class_name,
            "school_name": binding.class_info.school_name,
            "session": binding.class_info.session,
            "teacher_name": binding.class_info.teacher.real_name,
            "bind_time": binding.bind_time,
            "student_no_in_class": binding.student_no_in_class or "",
            "student_name": binding.name_in_class or student_profile.real_name  # 使用班级中的名字或档案名字
        })
    
    return classes


@router.post("/delete/{student_class_id}", response_model=dict)
async def delete_student(
    request: Request,
    student_class_id: int,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    # 从请求体中获取reason参数
    request_data = await request.json()
    reason = request_data.get('reason', '')
    if not reason:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="删除原因不能为空"
        )
    """删除学员"""
    try:
        result = await StudentService.delete_student(db, student_class_id, current_user.id, reason)
        
        # 记录系统操作日志
        await log_system_operation(
            db=db,
            request=request,
            user_id=current_user.id,
            action="删除学员",
            biz_id=student_class_id,
            request_params={
                "student_class_id": student_class_id,
                "reason": reason
            }
        )
        
        # 记录学员操作日志
        if result and 'old_student_info' in result and 'new_student_info' in result:
            old_student_info = result['old_student_info']
            new_student_info = result['new_student_info']
            from sqlalchemy import select
            from app.models.class_info import ClassInfo
            class_result = await db.execute(select(ClassInfo).where(ClassInfo.id == old_student_info['class_id']))
            class_info = class_result.scalar_one_or_none()
            class_name = class_info.class_name if class_info else "未知班级"
            
            await StudentOperationLogService.create_operation_log(
                operator_id=current_user.id,
                operator_name=current_user.real_name or current_user.username,
                class_id=old_student_info['class_id'],
                class_student_id=old_student_info['id'],
                class_name=class_name,
                student_name=old_student_info['name_in_class'],
                operation_type="delete",
                operation_content=f"删除学员：{old_student_info['name_in_class']}（原因：{reason}）",
                before_data=old_student_info,
                after_data=new_student_info,
                ip_address=request.client.host if request.client else None
            )
        
        return {
            "message": result["message"],
            **({"student_class_id": student_class_id} if result["status"] == "deleted" else {})
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/stop/{student_class_id}", response_model=dict)
async def stop_student(
    request: Request,
    student_class_id: int,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    # 从请求体中获取reason参数
    request_data = await request.json()
    reason = request_data.get('reason', '')
    if not reason:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="停用原因不能为空"
        )
    """停用学员（休学）"""
    try:
        result = await StudentService.stop_student(db, student_class_id, current_user.id, reason)
        
        # 记录系统操作日志
        await log_system_operation(
            db=db,
            request=request,
            user_id=current_user.id,
            action="停用学员",
            biz_id=student_class_id,
            request_params={
                "student_class_id": student_class_id,
                "reason": reason
            }
        )
        
        # 记录学员操作日志
        if result and 'old_student_info' in result and 'new_student_info' in result:
            old_student_info = result['old_student_info']
            new_student_info = result['new_student_info']
            from sqlalchemy import select
            from app.models.class_info import ClassInfo
            class_result = await db.execute(select(ClassInfo).where(ClassInfo.id == old_student_info['class_id']))
            class_info = class_result.scalar_one_or_none()
            class_name = class_info.class_name if class_info else "未知班级"
            
            await StudentOperationLogService.create_operation_log(
                operator_id=current_user.id,
                operator_name=current_user.real_name or current_user.username,
                class_id=old_student_info['class_id'],
                class_student_id=old_student_info['id'],
                class_name=class_name,
                student_name=old_student_info['name_in_class'],
                operation_type="stop",
                operation_content=f"停用学员：{old_student_info['name_in_class']}（原因：{reason}）",
                before_data=old_student_info,
                after_data=new_student_info,
                ip_address=request.client.host if request.client else None
            )
        
        return {
            "message": result["message"],
            **({"student_class_id": student_class_id} if result["status"] == "stopped" else {})
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/activate/{student_class_id}", response_model=dict)
async def activate_student(
    request: Request,
    student_class_id: int,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    """启用学员（复学）"""
    try:
        result = await StudentService.activate_student(db, student_class_id, current_user.id)
        
        # 记录系统操作日志
        await log_system_operation(
            db=db,
            request=request,
            user_id=current_user.id,
            action="启用学员",
            biz_id=student_class_id,
            request_params={
                "student_class_id": student_class_id
            }
        )
        
        # 记录学员操作日志
        if result and 'old_student_info' in result and 'new_student_info' in result:
            old_student_info = result['old_student_info']
            new_student_info = result['new_student_info']
            from sqlalchemy import select
            from app.models.class_info import ClassInfo
            class_result = await db.execute(select(ClassInfo).where(ClassInfo.id == old_student_info['class_id']))
            class_info = class_result.scalar_one_or_none()
            class_name = class_info.class_name if class_info else "未知班级"
            
            await StudentOperationLogService.create_operation_log(
                operator_id=current_user.id,
                operator_name=current_user.real_name or current_user.username,
                class_id=old_student_info['class_id'],
                class_student_id=old_student_info['id'],
                class_name=class_name,
                student_name=old_student_info['name_in_class'],
                operation_type="restore",
                operation_content=f"启用学员：{old_student_info['name_in_class']}",
                before_data=old_student_info,
                after_data=new_student_info,
                ip_address=request.client.host if request.client else None
            )
        
        return {
            "message": result["message"],
            **({"student_class_id": student_class_id} if result["status"] == "activated" else {})
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/unbind/{student_class_id}", response_model=dict)
async def unbind_student(
    request: Request,
    student_class_id: int,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    # 从请求体中获取reason参数
    request_data = await request.json()
    reason = request_data.get('reason', '')
    if not reason:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="解绑原因不能为空"
        )
    """解除绑定关系"""
    try:
        result = await StudentService.unbind_student(db, student_class_id, current_user.id, reason)
        
        # 记录系统操作日志
        await log_system_operation(
            db=db,
            request=request,
            user_id=current_user.id,
            action="解绑学员",
            biz_id=student_class_id,
            request_params={
                "student_class_id": student_class_id,
                "reason": reason
            }
        )
        
        # 记录学员操作日志
        if result and 'old_student_info' in result and 'new_student_info' in result:
            old_student_info = result['old_student_info']
            new_student_info = result['new_student_info']
            from sqlalchemy import select
            from app.models.class_info import ClassInfo
            class_result = await db.execute(select(ClassInfo).where(ClassInfo.id == old_student_info['class_id']))
            class_info = class_result.scalar_one_or_none()
            class_name = class_info.class_name if class_info else "未知班级"
            
            await StudentOperationLogService.create_operation_log(
                operator_id=current_user.id,
                operator_name=current_user.real_name or current_user.username,
                class_id=old_student_info['class_id'],
                class_student_id=old_student_info['id'],
                class_name=class_name,
                student_name=old_student_info['name_in_class'],
                operation_type="unbind",
                operation_content=f"解绑学员：{old_student_info['name_in_class']}（原因：{reason}）",
                before_data=old_student_info,
                after_data=new_student_info,
                ip_address=request.client.host if request.client else None
            )
        
        return {
            "message": result["message"],
            **({"student_class_id": student_class_id} if result["status"] == "unbound" else {})
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/class-students/{class_id}", response_model=List[StudentSimpleResponse])
async def get_class_students(
    class_id: int,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    """获取班级学员列表"""
    # 检查权限
    from app.services.class_service import ClassService
    class_info = await ClassService.get_class_by_id(db, class_id)
    if not class_info or class_info.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限查看此班级"
        )
    
    # 生成缓存键
    cache_key = f"students:class:{current_user.id}:{class_id}"
    
    # 尝试从缓存获取
    cached_result = await cache.get(cache_key)
    if cached_result:
        return cached_result
    
    students = await StudentService.get_teacher_students(db, current_user.id, class_id)
    
    # 缓存结果，5分钟过期
    await cache.set(cache_key, students, expire=300)
    
    return students


@router.get("/teacher-students")
async def get_teacher_students(
    class_id: Optional[int] = Query(None, description="班级ID"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    status: Optional[str] = Query(None, description="状态"),
    sort: Optional[str] = Query(None, description="排序字段"),
    order: Optional[str] = Query(None, description="排序顺序"),
    school_name: Optional[str] = Query(None, description="学校名称"),
    session: Optional[str] = Query(None, description="届别"),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=10000, description="返回的记录数"),
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    """获取导师的所有学员"""
    # 检查是否是超级管理员
    is_super_admin = current_user.role.role_name == "super_admin"
    result = await StudentService.get_teacher_students(
        db, current_user.id, class_id, keyword, status, sort, order, school_name, 
        session, is_super_admin, skip, limit
    )
    
    return result


@router.get("/search", response_model=List[dict])
async def search_students(
    keyword: str = Query(..., description="搜索关键词"),
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    """搜索学员（模糊匹配）"""
    students = await StudentService.search_students(db, current_user.id, keyword)
    return students


@router.get("/note/{class_student_id}", response_model=dict)
async def get_student_note(
    class_student_id: int,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    """获取学员备注"""
    note = await StudentService.get_student_note(db, class_student_id)
    if note:
        return {
            "id": note.id,
            "class_student_id": note.class_student_id,
            "real_name": note.real_name,
            "learning_characteristics": note.learning_characteristics,
            "personality_suggestions": note.personality_suggestions,
            "performance_summary": note.performance_summary,
            "tags": note.tags,
            "created_at": note.created_at,
            "updated_at": note.updated_at
        }
    else:
        return {
            "id": None,
            "class_student_id": class_student_id,
            "real_name": None,
            "learning_characteristics": None,
            "personality_suggestions": None,
            "performance_summary": None,
            "tags": None,
            "created_at": None,
            "updated_at": None
        }


@router.post("/note/{class_student_id}", response_model=dict)
async def create_or_update_student_note(
    class_student_id: int,
    note_data: StudentNoteCreate,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    """创建或更新学员备注"""
    # 获取更新前的备注
    old_note = await StudentService.get_student_note(db, class_student_id)
    old_note_data = {
        "real_name": old_note.real_name if old_note else None,
        "learning_characteristics": old_note.learning_characteristics if old_note else None,
        "personality_suggestions": old_note.personality_suggestions if old_note else None,
        "performance_summary": old_note.performance_summary if old_note else None,
        "tags": old_note.tags if old_note else None
    }

    # 更新备注
    note = await StudentService.create_or_update_student_note(
        db,
        class_student_id,
        note_data.learning_characteristics,
        note_data.personality_suggestions,
        note_data.performance_summary,
        note_data.real_name,
        note_data.tags
    )
    
    # 提交事务
    await db.commit()
    await db.refresh(note)
    
    # 检查备注是否有变化（不包括tags，因为tags由专门的标签API处理）
    note_changed = False
    if not old_note:
        # 新添加的备注，肯定有变化
        note_changed = True
        print(f"[DEBUG] 新添加备注，note_changed=True")
    else:
        # 检查每个字段是否有变化
        note_changed = (
            old_note.real_name != note.real_name or
            old_note.learning_characteristics != note.learning_characteristics or
            old_note.personality_suggestions != note.personality_suggestions or
            old_note.performance_summary != note.performance_summary
        )
    
    if note_changed:
        try:
            student_class = await StudentService.get_student_class_by_id(db, class_student_id)
            if student_class:
                operation_type = "note_add" if not old_note else "note_update"
                
                changes = []
                if not old_note:
                    if note.real_name:
                        changes.append(f"真实姓名：{note.real_name}")
                    if note.learning_characteristics:
                        changes.append(f"学习特征：{note.learning_characteristics[:20]}{'...' if len(note.learning_characteristics) > 20 else ''}")
                    if note.personality_suggestions:
                        changes.append(f"性格建议：{note.personality_suggestions[:20]}{'...' if len(note.personality_suggestions) > 20 else ''}")
                    if note.performance_summary:
                        changes.append(f"表现总结：{note.performance_summary[:20]}{'...' if len(note.performance_summary) > 20 else ''}")
                    
                    # 如果新备注没有任何内容，不记录日志
                    if not changes:
                        print(f"[DEBUG] 新备注为空，不记录日志")
                        return {
                            "id": note.id,
                            "class_student_id": note.class_student_id,
                            "real_name": note.real_name,
                            "learning_characteristics": note.learning_characteristics,
                            "personality_suggestions": note.personality_suggestions,
                            "performance_summary": note.performance_summary,
                            "tags": note.tags,
                            "created_at": note.created_at,
                            "updated_at": note.updated_at
                        }
                    
                    operation_content = f"添加学员 {student_class.name_in_class} 的备注"
                    if changes:
                        operation_content += f"，内容：{'；'.join(changes)}"
                else:
                    if old_note.real_name != note.real_name:
                        old_val = old_note.real_name or "（空）"
                        new_val = note.real_name or "（空）"
                        changes.append(f"真实姓名：{old_val}→{new_val}")
                    if old_note.learning_characteristics != note.learning_characteristics:
                        old_val = old_note.learning_characteristics or "（空）"
                        new_val = note.learning_characteristics or "（空）"
                        changes.append(f"学习特征：{old_val[:10]}→{new_val[:10]}{'...' if len(old_val) > 10 or len(new_val) > 10 else ''}")
                    if old_note.personality_suggestions != note.personality_suggestions:
                        old_val = old_note.personality_suggestions or "（空）"
                        new_val = note.personality_suggestions or "（空）"
                        changes.append(f"性格建议：{old_val[:10]}→{new_val[:10]}{'...' if len(old_val) > 10 or len(new_val) > 10 else ''}")
                    if old_note.performance_summary != note.performance_summary:
                        old_val = old_note.performance_summary or "（空）"
                        new_val = note.performance_summary or "（空）"
                        changes.append(f"表现总结：{old_val[:10]}→{new_val[:10]}{'...' if len(old_val) > 10 or len(new_val) > 10 else ''}")
                    operation_content = f"更新学员 {student_class.name_in_class} 的备注"
                    if changes:
                        operation_content += f"，变更：{'；'.join(changes)}"
                    else:
                        # 无实质变更，不记录日志
                        print(f"[DEBUG] 备注无实质变更，不记录日志")
                        return {
                            "id": note.id,
                            "class_student_id": note.class_student_id,
                            "real_name": note.real_name,
                            "learning_characteristics": note.learning_characteristics,
                            "personality_suggestions": note.personality_suggestions,
                            "performance_summary": note.performance_summary,
                            "tags": note.tags,
                            "created_at": note.created_at,
                            "updated_at": note.updated_at
                        }

                from sqlalchemy import select
                from app.models.class_info import ClassInfo
                class_result = await db.execute(select(ClassInfo).where(ClassInfo.id == student_class.class_id))
                class_info = class_result.scalar_one_or_none()
                class_name = class_info.class_name if class_info else "未知班级"
                
                await StudentOperationLogService.create_operation_log(
                    operator_id=current_user.id,
                    operator_name=current_user.real_name or current_user.username,
                    class_id=student_class.class_id,
                    class_student_id=student_class.id,
                    class_name=class_name,
                    student_name=student_class.name_in_class,
                    operation_type=operation_type,
                    operation_content=operation_content,
                    before_data=old_note_data,
                    after_data={
                        "real_name": note.real_name,
                        "learning_characteristics": note.learning_characteristics,
                        "personality_suggestions": note.personality_suggestions,
                        "performance_summary": note.performance_summary,
                        "tags": note.tags
                    }
                )
        except Exception as e:
            import traceback
            traceback.print_exc()
    
    return {
        "id": note.id,
        "class_student_id": note.class_student_id,
        "real_name": note.real_name,
        "learning_characteristics": note.learning_characteristics,
        "personality_suggestions": note.personality_suggestions,
        "performance_summary": note.performance_summary,
        "tags": note.tags,
        "created_at": note.created_at,
        "updated_at": note.updated_at
    }


class StudentTagsUpdate(BaseModel):
    tag_ids: List[int]


@router.get("/tags/{class_student_id}", response_model=List[dict])
async def get_student_tags(
    class_student_id: int,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    """获取学员标签"""
    tags = await StudentService.get_student_tags(db, class_student_id)
    return tags


@router.post("/tags/{class_student_id}", response_model=dict)
async def update_student_tags(
    class_student_id: int,
    tags_data: StudentTagsUpdate,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    """更新学员标签"""
    # 获取更新前的标签
    old_tags = await StudentService.get_student_tags(db, class_student_id)
    old_tag_names = [tag['name'] for tag in old_tags]
    
    # 获取新标签的名称（在更新之前查询，避免事务问题）
    from app.models.tag import Tag
    from sqlalchemy import select
    tag_ids = list(tags_data.tag_ids) if tags_data.tag_ids else []
    new_tag_names = []
    if len(tag_ids) > 0:
        tag_query = select(Tag.name).where(Tag.id.in_(tag_ids))
        tag_result = await db.execute(tag_query)
        new_tag_names = [row[0] for row in tag_result.all()]
    
    # 更新标签
    await StudentService.update_student_tags(db, class_student_id, tag_ids)
    
    # 提交事务
    await db.commit()
    
    # 清除相关缓存
    # 清除老师学员列表的所有缓存
    cache_pattern = f"students:teacher:{current_user.id}:*"
    await cache.clear_pattern(cache_pattern)
    
    # 记录学员操作日志
    try:
        student_class = await StudentService.get_student_class_by_id(db, class_student_id)
        if student_class:
            added_tags = [tag for tag in new_tag_names if tag not in old_tag_names]
            removed_tags = [tag for tag in old_tag_names if tag not in new_tag_names]
            
            # 只有当标签真正有变化时才记录日志
            if not added_tags and not removed_tags:
                print(f"[DEBUG] 标签无变化，不记录日志")
            elif added_tags:
                operation_type = "tag_add"
                operation_content = f"为学员 {student_class.name_in_class} 添加标签：{', '.join(added_tags)}"
                
                from sqlalchemy import select
                from app.models.class_info import ClassInfo
                class_result = await db.execute(select(ClassInfo).where(ClassInfo.id == student_class.class_id))
                class_info = class_result.scalar_one_or_none()
                class_name = class_info.class_name if class_info else "未知班级"
                
                await StudentOperationLogService.create_operation_log(
                    operator_id=current_user.id,
                    operator_name=current_user.real_name or current_user.username,
                    class_id=student_class.class_id,
                    class_student_id=student_class.id,
                    class_name=class_name,
                    student_name=student_class.name_in_class,
                    operation_type=operation_type,
                    operation_content=operation_content,
                    before_data={"tags": old_tag_names},
                    after_data={"tags": new_tag_names}
                )
            elif removed_tags:
                operation_type = "tag_delete"
                operation_content = f"为学员 {student_class.name_in_class} 删除标签：{', '.join(removed_tags)}"
                
                from sqlalchemy import select
                from app.models.class_info import ClassInfo
                class_result = await db.execute(select(ClassInfo).where(ClassInfo.id == student_class.class_id))
                class_info = class_result.scalar_one_or_none()
                class_name = class_info.class_name if class_info else "未知班级"
                
                await StudentOperationLogService.create_operation_log(
                    operator_id=current_user.id,
                    operator_name=current_user.real_name or current_user.username,
                    class_id=student_class.class_id,
                    class_student_id=student_class.id,
                    class_name=class_name,
                    student_name=student_class.name_in_class,
                    operation_type=operation_type,
                    operation_content=operation_content,
                    before_data={"tags": old_tag_names},
                    after_data={"tags": new_tag_names}
                )
    except Exception as log_error:
        print(f"记录学员操作日志失败: {str(log_error)}")
    
    return {"message": "标签更新成功"}


class StudentInfoUpdate(BaseModel):
    real_name: str


@router.put("/{class_student_id}", response_model=dict)
async def update_student_info(
    request: Request,
    class_student_id: int,
    student_data: StudentInfoUpdate,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    """更新学员基本信息"""
    try:
        result = await StudentService.update_student_info(
            db,
            class_student_id,
            current_user.id,
            student_data.real_name
        )
        
        # 记录系统操作日志
        await log_system_operation(
            db=db,
            request=request,
            user_id=current_user.id,
            action="更新学员信息",
            biz_id=class_student_id,
            request_params={
                "class_student_id": class_student_id,
                "real_name": student_data.real_name
            }
        )
        
        # 记录学员操作日志
        if result and 'old_student_info' in result and 'new_student_info' in result:
            old_student_info = result['old_student_info']
            new_student_info = result['new_student_info']
            from sqlalchemy import select
            from app.models.class_info import ClassInfo
            class_result = await db.execute(select(ClassInfo).where(ClassInfo.id == old_student_info['class_id']))
            class_info = class_result.scalar_one_or_none()
            class_name = class_info.class_name if class_info else "未知班级"
            
            await StudentOperationLogService.create_operation_log(
                operator_id=current_user.id,
                operator_name=current_user.real_name or current_user.username,
                class_id=old_student_info['class_id'],
                class_student_id=old_student_info['id'],
                class_name=class_name,
                student_name=new_student_info['name_in_class'],
                operation_type="update_info",
                operation_content=f"更新学员姓名：{old_student_info['name_in_class']} → {new_student_info['name_in_class']}",
                before_data=old_student_info,
                after_data=new_student_info,
                ip_address=request.client.host if request.client else None
            )
        
        return {
            "message": result["message"],
            **({"student_class_id": class_student_id} if result["status"] == "updated" else {})
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )



