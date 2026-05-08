from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from app.core.database import get_db
from app.core.security import require_admin
from app.models.user import User
from app.models.class_info import ClassInfo
from app.models.class_student import ClassStudent
from app.models.student_profile import StudentProfile
from app.models.growth_log import Growth
from app.models.student_operation_log import StudentOperationLog
from sqlalchemy.orm import selectinload

router = APIRouter()


@router.get("/students")
async def get_admin_students(
    class_id: Optional[int] = Query(None, description="班级ID"),
    bind_status: Optional[str] = Query(None, description="绑定状态"),
    is_deleted: Optional[bool] = Query(None, description="是否删除"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取学员列表（管理员）"""
    query = select(ClassStudent).options(
        selectinload(ClassStudent.class_info),
        selectinload(ClassStudent.student_profile).selectinload(StudentProfile.user)
    )
    
    if class_id:
        query = query.where(ClassStudent.class_id == class_id)
    if bind_status:
        query = query.where(ClassStudent.bind_status == bind_status)
    if is_deleted is not None:
        query = query.where(ClassStudent.is_deleted == is_deleted)
    if keyword:
        query = query.where(ClassStudent.name_in_class.contains(keyword))
    
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0
    
    query = query.order_by(ClassStudent.created_at.desc()).offset(skip).limit(limit)
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
            "class_id": student.class_id,
            "class_name": student.class_info.class_name if student.class_info else "-",
            "bind_status": student.bind_status.value if student.bind_status else None,
            "is_deleted": student.is_deleted,
            "created_at": student.created_at
        })
    
    return {
        "items": student_list,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/students/{student_id}")
async def get_student_detail(
    student_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取学员详情"""
    student = await db.execute(
        select(ClassStudent)
        .options(
            selectinload(ClassStudent.class_info),
            selectinload(ClassStudent.student_profile).selectinload(StudentProfile.user)
        )
        .where(ClassStudent.id == student_id)
    )
    student = student.scalar_one_or_none()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学员不存在"
        )
    
    name = ""
    user_id = None
    if student.student_profile and student.student_profile.user:
        name = student.student_profile.user.real_name
        user_id = student.student_profile.user.id
    
    return {
        "id": student.id,
        "name": name,
        "user_id": user_id,
        "name_in_class": student.name_in_class,
        "class_id": student.class_id,
        "class_name": student.class_info.class_name if student.class_info else "-",
        "bind_status": student.bind_status.value if student.bind_status else None,
        "is_deleted": student.is_deleted,
        "created_at": student.created_at
    }


@router.post("/students/{student_id}/unbind")
async def force_unbind_student(
    student_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """强制解绑学员"""
    from app.models.system_log import SystemLog, LogType, LogLevel
    
    student = await db.get(ClassStudent, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学员不存在"
        )
    
    if not student.student_profile_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该学员未绑定账号"
        )
    
    old_profile_id = student.student_profile_id
    student.student_profile_id = None
    student.bind_status = None
    
    system_log = SystemLog(
        user_id=current_user.id,
        username=current_user.username,
        real_name=current_user.real_name,
        log_type=LogType.UPDATE,
        log_level=LogLevel.INFO,
        module="学员管理",
        action="强制解绑学员",
        biz_type="student",
        biz_id=student_id,
        request_params=f'{{"student_id": {student_id}, "old_profile_id": {old_profile_id}}}'
    )
    db.add(system_log)
    
    await db.commit()
    
    return {"message": "解绑成功"}


@router.delete("/students/{student_id}")
async def force_delete_student(
    student_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """强制删除学员"""
    from sqlalchemy import text
    from app.models.system_log import SystemLog, LogType, LogLevel
    
    result = await db.execute(text("SELECT name_in_class, student_no_in_class, class_id FROM class_student WHERE id = :student_id"), {"student_id": student_id})
    student_data = result.first()
    if not student_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学员不存在"
        )
    
    student_name = student_data[0]
    student_no = student_data[1]
    class_id = student_data[2]
    
    class_name = ""
    if class_id:
        class_result = await db.execute(text("SELECT class_name FROM class_info WHERE id = :class_id"), {"class_id": class_id})
        class_data = class_result.first()
        if class_data:
            class_name = class_data[0]
    
    tables_to_delete = [
        "wish",
        "gift_order_log", 
        "gift_order",
        "student_tag",
        "student_note",
        "growth",
        "student_operation_log"
    ]
    
    try:
        for table in tables_to_delete:
            try:
                await db.execute(text(f"DELETE FROM {table} WHERE class_student_id = :student_id"), {"student_id": student_id})
            except Exception as e:
                print(f"Error deleting from {table}: {e}")
        
        await db.execute(text("DELETE FROM class_student WHERE id = :student_id"), {"student_id": student_id})
        
        system_log = SystemLog(
            user_id=current_user.id,
            username=current_user.username,
            real_name=current_user.real_name,
            log_type=LogType.DELETE,
            log_level=LogLevel.INFO,
            module="学员管理",
            action="强制删除学员",
            biz_type="student",
            biz_id=student_id,
            request_params=f'{{"student_id": {student_id}, "student_name": "{student_name}", "student_no": "{student_no}", "class_id": {class_id}, "class_name": "{class_name}"}}',
            before_data=f'{{"学员姓名": "{student_name}", "学号": "{student_no}", "班级ID": {class_id}, "班级名称": "{class_name}"}}'
        )
        db.add(system_log)
        
        await db.commit()
        
        return {"message": "删除成功"}
    except Exception as e:
        await db.rollback()
        print(f"Delete student error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除学员失败: {str(e)}"
        )


@router.get("/students/{student_id}/growth-records")
async def get_student_growth_records(
    student_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取学员成长记录"""
    student = await db.get(ClassStudent, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学员不存在"
        )
    
    query = select(Growth).where(Growth.class_student_id == student_id)
    
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0
    
    query = query.order_by(Growth.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    records = result.scalars().all()
    
    record_list = []
    for record in records:
        operator = await db.get(User, record.operator_id) if record.operator_id else None
        
        record_list.append({
            "id": record.id,
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


@router.get("/students/{student_id}/logs")
async def get_student_logs(
    student_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取学员操作日志"""
    student = await db.get(ClassStudent, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学员不存在"
        )
    
    query = select(StudentOperationLog).where(StudentOperationLog.class_student_id == student_id)
    
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0
    
    query = query.order_by(StudentOperationLog.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    logs = result.scalars().all()
    
    log_list = []
    for log in logs:
        operator = await db.get(User, log.operator_id) if log.operator_id else None
        
        log_list.append({
            "id": log.id,
            "operation_type": log.operation_type,
            "description": log.description,
            "operator_name": operator.real_name if operator else "-",
            "created_at": log.created_at
        })
    
    return {
        "items": log_list,
        "total": total,
        "skip": skip,
        "limit": limit
    }
