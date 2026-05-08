from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from app.core.database import get_db
from app.core.security import require_admin
from app.models.user import User
from app.models.class_info import ClassInfo
from app.models.class_student import ClassStudent
from app.models.class_assistant import ClassAssistant
from app.models.growth_log import Growth
from app.models.student_profile import StudentProfile
from sqlalchemy.orm import selectinload

router = APIRouter()


@router.get("/classes")
async def get_admin_classes(
    class_name: Optional[str] = Query(None, description="班级名称"),
    status: Optional[bool] = Query(None, description="班级状态"),
    grade: Optional[int] = Query(None, description="年级"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    query = select(ClassInfo).options(
        selectinload(ClassInfo.teacher)
    )
    
    if class_name:
        query = query.where(ClassInfo.class_name.contains(class_name))
    if status is not None:
        query = query.where(ClassInfo.status == status)
    if grade is not None:
        query = query.where(ClassInfo.school_name.contains(str(grade)))
    if keyword:
        query = query.where(
            ClassInfo.class_name.contains(keyword) |
            ClassInfo.school_name.contains(keyword) |
            ClassInfo.session.contains(keyword)
        )
    
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0
    
    query = query.order_by(ClassInfo.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    classes = result.scalars().all()
    
    class_list = []
    for cls in classes:
        teacher_name = cls.teacher.real_name if cls.teacher else "-"
        
        student_count = await db.execute(
            select(func.count()).select_from(ClassStudent).where(ClassStudent.class_id == cls.id)
        )
        student_count = student_count.scalar() or 0
        
        class_list.append({
            "id": cls.id,
            "school_name": cls.school_name,
            "session": cls.session,
            "class_name": cls.class_name,
            "teacher_name": teacher_name,
            "student_count": student_count,
            "status": cls.status,
            "created_at": cls.created_at,
            "updated_at": cls.updated_at
        })
    
    return {
        "items": class_list,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/classes/{class_id}")
async def get_class_detail(
    class_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    cls = await db.execute(
        select(ClassInfo)
        .options(selectinload(ClassInfo.teacher))
        .where(ClassInfo.id == class_id)
    )
    cls = cls.scalar_one_or_none()
    
    if not cls:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="班级不存在"
        )
    
    teacher_name = cls.teacher.real_name if cls.teacher else "-"
    
    student_count = await db.execute(
        select(func.count()).select_from(ClassStudent).where(ClassStudent.class_id == class_id)
    )
    student_count = student_count.scalar() or 0
    
    return {
        "id": cls.id,
        "school_name": cls.school_name,
        "session": cls.session,
        "class_name": cls.class_name,
        "teacher_name": teacher_name,
        "student_count": student_count,
        "status": cls.status,
        "created_at": cls.created_at,
        "updated_at": cls.updated_at
    }


@router.put("/classes/{class_id}/status")
async def update_class_status(
    class_id: int,
    status: bool,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    from app.models.system_log import SystemLog, LogType, LogLevel
    
    cls = await db.get(ClassInfo, class_id)
    if not cls:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="班级不存在"
        )
    
    old_status = cls.status
    cls.status = status
    
    system_log = SystemLog(
        user_id=current_user.id,
        username=current_user.username,
        real_name=current_user.real_name,
        log_type=LogType.UPDATE,
        log_level=LogLevel.INFO,
        module="班级管理",
        action="更新班级状态",
        biz_type="class",
        biz_id=class_id,
        request_params=f'{{"class_id": {class_id}, "status": {status}}}',
        before_data=f'{{"班级名称": "{cls.class_name}", "原状态": {old_status}, "新状态": {status}}}'
    )
    db.add(system_log)
    
    await db.commit()
    
    return {"message": "状态更新成功"}


@router.get("/classes/{class_id}/students")
async def get_class_students(
    class_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    cls = await db.get(ClassInfo, class_id)
    if not cls:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="班级不存在"
        )
    
    query = select(ClassStudent).options(
        selectinload(ClassStudent.student_profile).selectinload(StudentProfile.user)
    ).where(ClassStudent.class_id == class_id)
    
    result = await db.execute(query)
    students = result.scalars().all()
    
    student_list = []
    for student in students:
        name = ""
        if student.student_profile and student.student_profile.user:
            name = student.student_profile.user.real_name
        
        student_list.append({
            "id": student.id,
            "name": name,
            "name_in_class": student.name_in_class,
            "bind_status": student.bind_status.value if student.bind_status else None,
            "created_at": student.created_at
        })
    
    return {
        "items": student_list,
        "total": len(student_list)
    }


@router.get("/classes/{class_id}/growth-records")
async def get_class_growth_records(
    class_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    cls = await db.get(ClassInfo, class_id)
    if not cls:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="班级不存在"
        )
    
    query = select(Growth).options(
        selectinload(Growth.class_student)
    ).where(Growth.class_id == class_id)
    
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0
    
    query = query.order_by(Growth.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    records = result.scalars().all()
    
    record_list = []
    for record in records:
        student_name = record.class_student.name_in_class if record.class_student else "-"
        operator = await db.get(User, record.operator_id) if record.operator_id else None
        
        record_list.append({
            "id": record.id,
            "student_name": student_name,
            "change_value": record.change_value,
            "reason": record.reason,
            "operator_name": operator.real_name if operator else "-",
            "created_at": record.created_at
        })
    
    return {
        "items": record_list,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.delete("/classes/{class_id}")
async def delete_class(
    class_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    from sqlalchemy import text
    from app.models.system_log import SystemLog, LogType, LogLevel
    
    cls = await db.get(ClassInfo, class_id)
    if not cls:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="班级不存在"
        )
    
    class_name = cls.class_name
    
    tables_to_delete = [
        "wish",
        "gift_order_log",
        "gift_order",
        "student_tag",
        "student_note",
        "growth",
        "student_operation_log",
        "class_student",
        "class_assistant"
    ]
    
    try:
        for table in tables_to_delete:
            await db.execute(text(f"DELETE FROM {table} WHERE class_id = :class_id"), {"class_id": class_id})
        
        await db.delete(cls)
        
        system_log = SystemLog(
            user_id=current_user.id,
            username=current_user.username,
            real_name=current_user.real_name,
            log_type=LogType.DELETE,
            log_level=LogLevel.INFO,
            module="班级管理",
            action="删除班级",
            biz_type="class",
            biz_id=class_id,
            request_params=f'{{"class_id": {class_id}}}',
            before_data=f'{{"班级名称": "{class_name}"}}'
        )
        db.add(system_log)
        
        await db.commit()
        
        return {"message": "删除成功"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除班级失败: {str(e)}"
        )


@router.get("/classes/{class_id}/assistants")
async def get_class_assistants(
    class_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    cls = await db.get(ClassInfo, class_id)
    if not cls:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="班级不存在"
        )
    
    query = select(ClassAssistant).options(
        selectinload(ClassAssistant.user)
    ).where(ClassAssistant.class_id == class_id)
    
    result = await db.execute(query)
    assistants = result.scalars().all()
    
    assistant_list = []
    for assistant in assistants:
        assistant_list.append({
            "id": assistant.id,
            "class_id": assistant.class_id,
            "user_id": assistant.user_id,
            "real_name": assistant.user.real_name if assistant.user else "-",
            "username": assistant.user.username if assistant.user else "-",
            "created_at": assistant.created_at
        })
    
    return {
        "items": assistant_list,
        "total": len(assistant_list)
    }


@router.post("/classes/{class_id}/assistants")
async def add_class_assistant(
    class_id: int,
    user_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    cls = await db.get(ClassInfo, class_id)
    if not cls:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="班级不存在"
        )
    
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    existing = await db.execute(
        select(ClassAssistant).where(ClassAssistant.class_id == class_id, ClassAssistant.user_id == user_id)
    )
    existing = existing.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该用户已是班级助教"
        )
    
    assistant = ClassAssistant(
        class_id=class_id,
        user_id=user_id
    )
    db.add(assistant)
    
    from app.models.system_log import SystemLog, LogType, LogLevel
    system_log = SystemLog(
        user_id=current_user.id,
        username=current_user.username,
        real_name=current_user.real_name,
        log_type=LogType.CREATE,
        log_level=LogLevel.INFO,
        module="班级管理",
        action="添加助教",
        biz_type="assistant",
        biz_id=assistant.id,
        request_params=f'{{"class_id": {class_id}, "user_id": {user_id}}}'
    )
    db.add(system_log)
    
    await db.commit()
    
    return {"message": "添加成功"}


@router.delete("/classes/{class_id}/assistants/{assistant_id}")
async def remove_class_assistant(
    class_id: int,
    assistant_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    assistant = await db.get(ClassAssistant, assistant_id)
    if not assistant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="助教记录不存在"
        )
    
    if assistant.class_id != class_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="助教不属于该班级"
        )
    
    await db.delete(assistant)
    
    from app.models.system_log import SystemLog, LogType, LogLevel
    system_log = SystemLog(
        user_id=current_user.id,
        username=current_user.username,
        real_name=current_user.real_name,
        log_type=LogType.DELETE,
        log_level=LogLevel.INFO,
        module="班级管理",
        action="移除助教",
        biz_type="assistant",
        biz_id=assistant_id,
        request_params=f'{{"class_id": {class_id}, "assistant_id": {assistant_id}}}'
    )
    db.add(system_log)
    
    await db.commit()
    
    return {"message": "移除成功"}
