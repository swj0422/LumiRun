from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel
from app.core.database import get_db
from app.core.security import get_current_user, require_teacher
from app.models.user import User
from app.models.class_info import ClassInfo
from app.services import class_student_service
from app.services.class_service import ClassService
from app.core.cache import cache
from app.services.log_service import LogService
from app.services.student_operation_log_service import StudentOperationLogService
from app.models.system_log import LogType, LogLevel
from app.core.logger import logger

router = APIRouter(prefix="/class-students", tags=["班级学员管理"])


class StudentCreate(BaseModel):
    class_id: int
    student_no: str
    real_name: str


class StudentBatchCreate(BaseModel):
    class_id: int
    students: List[dict]


class StudentUpdate(BaseModel):
    student_no: str
    real_name: str


class StudentResponse(BaseModel):
    id: int
    class_id: int
    student_no: Optional[str]
    real_name: str
    user_id: Optional[int]
    status: int
    bind_time: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


@router.post("/", response_model=StudentResponse)
async def add_student(
    request: Request,
    data: StudentCreate,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    class_info = await ClassService.get_class_by_id(db, data.class_id)
    if not class_info:
        raise HTTPException(status_code=404, detail="班级不存在")
    if class_info.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="只能管理自己创建的班级")
    
    try:
        # 记录添加学员请求
        logger.info(f"添加学员请求: class_id={data.class_id}, student_no={data.student_no}, real_name={data.real_name}")
        
        student = await class_student_service.ClassStudentService.add_student(
            db, data.class_id, data.student_no, data.real_name
        )
        
        # 清除相关缓存
        try:
            cache_pattern = f"students:teacher:{current_user.id}:*"
            await cache.clear_pattern(cache_pattern)
            logger.info(f"清除缓存: {cache_pattern}")
        except Exception as cache_error:
            logger.error(f"清除缓存失败: {str(cache_error)}")
        
        # 记录操作日志
        try:
            await LogService.create_log(
                db=db,
                user_id=current_user.id,
                log_type=LogType.OPERATION,
                log_level=LogLevel.INFO,
                module="学员管理",
                action="添加学员",
                biz_type="student",
                biz_id=student.id,
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                request_url=str(request.url),
                request_method=request.method,
                request_params={
                    "class_id": data.class_id,
                    "student_no": data.student_no,
                    "real_name": data.real_name
                },
                response_status=200
            )
            logger.info("操作日志记录成功")
        except Exception as log_error:
            logger.error(f"记录操作日志失败: {str(log_error)}")
        
        # 记录学员操作日志
        try:
            await StudentOperationLogService.create_operation_log(
                db,
                current_user.id,
                current_user.real_name or current_user.username,
                data.class_id,
                student.id,
                data.real_name,
                "add",
                f"添加学员：{data.real_name}（学号：{data.student_no}）",
                None,
                {
                    "class_id": data.class_id,
                    "student_no": data.student_no,
                    "real_name": data.real_name
                },
                request.client.host if request.client else None
            )
            logger.info("学员操作日志记录成功")
        except Exception as log_error:
            logger.error(f"记录学员操作日志失败: {str(log_error)}")
        
        return StudentResponse(
            id=student.id,
            class_id=student.class_id,
            student_no=student.student_no_in_class,
            real_name=student.name_in_class,
            user_id=student.student_profile_id,
            status=0,
            bind_time=student.bind_time.isoformat() if student.bind_time else None,
            created_at=student.created_at.isoformat() if student.created_at else None
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"添加学员失败: {str(e)}")
        raise HTTPException(status_code=500, detail="添加学员失败，请重试")


@router.post("/batch", response_model=dict)
async def batch_add_students(
    request: Request,
    data: StudentBatchCreate,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    class_info = await ClassService.get_class_by_id(db, data.class_id)
    if not class_info:
        raise HTTPException(status_code=404, detail="班级不存在")
    if class_info.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="只能管理自己创建的班级")
    
    try:
        # 记录批量添加学员请求
        logger.info(f"批量添加学员请求: class_id={data.class_id}, count={len(data.students)}")
        
        # 转换学生数据格式
        formatted_students = []
        for student_data in data.students:
            formatted_students.append({
                "student_no_in_class": student_data.get("student_no"),
                "name_in_class": student_data.get("real_name")
            })
        
        students = await class_student_service.ClassStudentService.batch_add_students(
            db, data.class_id, formatted_students
        )
        
        # 清除相关缓存
        try:
            cache_pattern = f"students:teacher:{current_user.id}:*"
            await cache.clear_pattern(cache_pattern)
            logger.info(f"清除缓存: {cache_pattern}")
        except Exception as cache_error:
            logger.error(f"清除缓存失败: {str(cache_error)}")
        
        # 记录操作日志
        try:
            await LogService.create_log(
                db=db,
                user_id=current_user.id,
                log_type=LogType.OPERATION,
                log_level=LogLevel.INFO,
                module="学员管理",
                action="批量添加学员",
                biz_type="student",
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                request_url=str(request.url),
                request_method=request.method,
                request_params={
                    "class_id": data.class_id,
                    "count": len(students)
                },
                response_status=200
            )
            logger.info("操作日志记录成功")
        except Exception as log_error:
            logger.error(f"记录操作日志失败: {str(log_error)}")
        
        # 记录学员操作日志
        try:
            for student in students:
                await StudentOperationLogService.create_operation_log(
                    db,
                    current_user.id,
                    current_user.real_name or current_user.username,
                    data.class_id,
                    student.id,
                    student.name_in_class,
                    "add",
                    f"批量添加学员：{student.name_in_class}（学号：{student.student_no_in_class}）",
                    None,
                    {
                        "class_id": data.class_id,
                        "student_no": student.student_no_in_class,
                        "real_name": student.name_in_class
                    },
                    request.client.host if request.client else None
                )
            logger.info("学员操作日志记录成功")
        except Exception as log_error:
            logger.error(f"记录学员操作日志失败: {str(log_error)}")
        
        return {"message": "批量添加成功", "count": len(students)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"批量添加学员失败: {str(e)}")
        raise HTTPException(status_code=500, detail="批量添加学员失败，请重试")


@router.get("/class/{class_id}", response_model=List[StudentResponse])
async def get_class_students(
    class_id: int,
    status: Optional[int] = None,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    class_info = await ClassService.get_class_by_id(db, class_id)
    if not class_info:
        raise HTTPException(status_code=404, detail="班级不存在")
    if class_info.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="只能管理自己创建的班级")
    
    students = await class_student_service.ClassStudentService.get_students_by_class(db, class_id)
    
    # 转换为响应格式
    result = []
    for student in students:
        result.append(StudentResponse(
            id=student.id,
            class_id=student.class_id,
            student_no=student.student_no_in_class,
            real_name=student.name_in_class,
            user_id=student.student_profile_id,
            status=0,
            bind_time=student.bind_time.isoformat() if student.bind_time else None,
            created_at=student.created_at.isoformat() if student.created_at else None
        ))
    return result


@router.post("/{student_id}/switch-class")
async def switch_student_class(
    student_id: int,
    new_class_id: int,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    """学员切换班级"""
    # 获取学员信息
    student = await class_student_service.ClassStudentService.get_student_by_id(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="学员不存在")
    
    # 验证权限：确保导师只能管理自己的班级
    old_class = await ClassService.get_class_by_id(db, student.class_id)
    new_class = await ClassService.get_class_by_id(db, new_class_id)
    
    if not old_class or old_class.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权管理该学员")
    
    if not new_class or new_class.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权管理目标班级")
    
    try:
        new_student = await class_student_service.ClassStudentService.switch_class(
            db, student_id, new_class_id
        )
        return {
            "message": "班级切换成功",
            "student_id": new_student.id,
            "class_id": new_student.class_id,
            "class_name": new_class.class_name
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: int,
    data: StudentUpdate,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    """更新学员信息"""
    # 获取学员信息
    student = await class_student_service.ClassStudentService.get_student_by_id(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="学员不存在")
    
    # 验证权限：确保导师只能管理自己的班级
    class_info = await ClassService.get_class_by_id(db, student.class_id)
    if not class_info or class_info.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权管理该学员")
    
    try:
        # 更新学员信息
        updated_student = await class_student_service.ClassStudentService.update_student(
            db, student_id, data.student_no, data.real_name
        )
        
        # 清除相关缓存
        try:
            cache_pattern = f"students:teacher:{current_user.id}:*"
            await cache.clear_pattern(cache_pattern)
            logger.info(f"清除缓存: {cache_pattern}")
        except Exception as cache_error:
            logger.error(f"清除缓存失败: {str(cache_error)}")
        
        return StudentResponse(
            id=updated_student.id,
            class_id=updated_student.class_id,
            student_no=updated_student.student_no_in_class,
            real_name=updated_student.name_in_class,
            user_id=updated_student.student_profile_id,
            status=0,
            bind_time=updated_student.bind_time.isoformat() if updated_student.bind_time else None,
            created_at=updated_student.created_at.isoformat() if updated_student.created_at else None
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"更新学员失败: {str(e)}")
        raise HTTPException(status_code=500, detail="更新学员失败，请重试")


@router.put("/{student_id}/stop")
async def stop_student(
    request: Request,
    student_id: int,
    data: dict,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    reason = data.get("reason", "")
    if not reason:
        raise HTTPException(status_code=400, detail="请输入停用原因")
    """停用学员"""
    # 获取学员信息
    student = await class_student_service.ClassStudentService.get_student_by_id(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="学员不存在")
    
    # 验证权限：确保导师只能管理自己的班级
    class_info = await ClassService.get_class_by_id(db, student.class_id)
    if not class_info or class_info.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权管理该学员")
    
    try:
        # 停用学员
        student.is_active = False
        await db.commit()
        
        # 清除相关缓存
        try:
            cache_pattern = f"students:teacher:{current_user.id}:*"
            await cache.clear_pattern(cache_pattern)
            logger.info(f"清除缓存: {cache_pattern}")
        except Exception as cache_error:
            logger.error(f"清除缓存失败: {str(cache_error)}")
        
        # 记录学员操作日志
        try:
            await StudentOperationLogService.create_operation_log(
                db,
                current_user.id,
                current_user.real_name or current_user.username,
                student.class_id,
                student.id,
                student.name_in_class,
                "stop",
                f"停用学员：{student.name_in_class}，原因：{reason}",
                {
                    "is_active": True
                },
                {
                    "is_active": False,
                    "reason": reason
                },
                request.client.host if request.client else None
            )
            logger.info("学员操作日志记录成功")
        except Exception as log_error:
            logger.error(f"记录学员操作日志失败: {str(log_error)}")
        
        return {"message": "停用成功"}
    except Exception as e:
        logger.error(f"停用学员失败: {str(e)}")
        raise HTTPException(status_code=500, detail="停用学员失败，请重试")
