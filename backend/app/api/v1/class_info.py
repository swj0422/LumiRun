from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.core.database import get_db
from app.core.security import get_current_user, require_manager, require_admin
from app.schemas.class_info import ClassCreate, ClassUpdate, ClassStatusUpdate
from app.services.class_service import ClassService
from app.models.user import User
from app.core.logger import logger

router = APIRouter()


@router.get("/", response_model=dict)
async def get_classes(
    status: Optional[bool] = Query(None, description="班级状态"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取班级列表"""
    from sqlalchemy import select, func
    from app.models.class_info import ClassInfo
    
    if current_user.role.role_name in ["super_admin", "admin"]:
        # 管理员查看所有班级
        base_query = select(ClassInfo)
        if status is not None:
            base_query = base_query.where(ClassInfo.status == status)
        
        # 获取总数
        count_query = select(func.count()).select_from(base_query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0
        
        # 获取数据
        query = base_query.order_by(ClassInfo.created_at.desc())
        result = await db.execute(query)
        classes = result.scalars().all()
    else:
        # 检查是否是班级助理
        from app.services.class_assistant_service import ClassAssistantService
        from app.models.class_assistant import ClassAssistant
        
        # 先获取导师自己的班级
        teacher_query = select(ClassInfo).where(ClassInfo.teacher_id == current_user.id)
        if status is not None:
            teacher_query = teacher_query.where(ClassInfo.status == status)
        
        # 获取班级助理被授权的班级
        assistant_classes = await ClassAssistantService.get_user_assistant_classes(db, current_user.id)
        assistant_class_ids = [cls.id for cls in assistant_classes]
        
        # 如果是班级助理，添加被授权的班级
        if assistant_class_ids:
            assistant_query = select(ClassInfo).where(ClassInfo.id.in_(assistant_class_ids))
            if status is not None:
                assistant_query = assistant_query.where(ClassInfo.status == status)
            
            # 执行两个查询
            teacher_result = await db.execute(teacher_query)
            assistant_result = await db.execute(assistant_query)
            
            # 合并结果，去重
            teacher_classes = teacher_result.scalars().all()
            assistant_classes = assistant_result.scalars().all()
            
            # 去重
            class_id_set = set()
            classes = []
            
            for cls in teacher_classes:
                if cls.id not in class_id_set:
                    class_id_set.add(cls.id)
                    classes.append(cls)
            
            for cls in assistant_classes:
                if cls.id not in class_id_set:
                    class_id_set.add(cls.id)
                    classes.append(cls)
        else:
            # 不是班级助理，只查看自己的班级
            teacher_result = await db.execute(teacher_query)
            classes = teacher_result.scalars().all()
        
        total = len(classes)
    
    # 构建返回数据
    class_list = []
    for cls in classes:
        student_count = await ClassService.get_class_student_count(db, cls.id)
        class_list.append({
            "id": cls.id,
            "school_name": cls.school_name,
            "session": cls.session,
            "class_name": cls.class_name,
            "description": cls.description,
            "teacher_id": cls.teacher_id,
            "teacher_name": "",  # 暂时使用空字符串，避免访问关系字段
            "status": cls.status,
            "qr_code": cls.qr_code,
            "qr_url": cls.qr_url,
            "student_count": student_count,
            "created_at": cls.created_at,
            "updated_at": cls.updated_at
        })
    
    return {
        "items": class_list,
        "total": total
    }


@router.get("/qr/{qr_code}", response_model=dict)
async def get_class_by_qr(
    qr_code: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """根据二维码获取班级信息"""
    class_info = await ClassService.get_class_by_qr_code(db, qr_code)

    if not class_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="班级不存在或二维码无效"
        )

    student_count = await ClassService.get_class_student_count(db, class_info.id)

    return {
        "id": class_info.id,
        "school_name": class_info.school_name,
        "session": class_info.session,
        "class_name": class_info.class_name,
        "description": class_info.description,
        "teacher_id": class_info.teacher_id,
        "teacher_name": class_info.teacher.real_name if class_info.teacher else "",
        "status": class_info.status,
        "qr_code": class_info.qr_code,
        "qr_url": class_info.qr_url,
        "student_count": student_count,
        "created_at": class_info.created_at,
        "updated_at": class_info.updated_at
    }


@router.get("/{class_id}", response_model=dict)
async def get_class(
    class_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取班级详情"""
    class_info = await ClassService.get_class_by_id(db, class_id)
    
    if not class_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="班级不存在"
        )
    
    # 权限检查：管理员可查看所有班级，导师只能查看自己的班级，班级助理只能查看被授权的班级
    from app.services.class_assistant_service import ClassAssistantService
    if current_user.role.role_name not in ["super_admin", "admin"]:
        # 检查是否是班级的创建者
        if class_info.teacher_id != current_user.id:
            # 检查是否是班级的助理
            is_assistant = await ClassAssistantService.is_assistant_of_class(db, current_user.id, class_id)
            if not is_assistant:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="无权限查看此班级"
                )
    
    student_count = await ClassService.get_class_student_count(db, class_info.id)
    
    return {
        "id": class_info.id,
        "school_name": class_info.school_name,
        "session": class_info.session,
        "class_name": class_info.class_name,
        "description": class_info.description,
        "teacher_id": class_info.teacher_id,
        "teacher_name": class_info.teacher.real_name if class_info.teacher else "",
        "status": class_info.status,
        "qr_code": class_info.qr_code,
        "qr_url": class_info.qr_url,
        "student_count": student_count,
        "created_at": class_info.created_at,
        "updated_at": class_info.updated_at
    }


@router.post("/", response_model=dict)
async def create_class(
    class_data: ClassCreate,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """创建班级（导师）"""
    try:
        class_info = await ClassService.create_class(db, class_data, current_user.id)
        return {
            "message": "班级创建成功",
            "class_id": class_info.id,
            "qr_code": class_info.qr_code
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{class_id}", response_model=dict)
async def update_class(
    class_id: int,
    class_data: ClassUpdate,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """更新班级（仅名称）"""
    class_info = await ClassService.get_class_by_id(db, class_id)
    
    if not class_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="班级不存在"
        )
    
    # 权限检查：只能更新自己的班级
    if class_info.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能更新自己创建的班级"
        )
    
    try:
        class_info = await ClassService.update_class(db, class_info, class_data)
        return {
            "message": "班级更新成功",
            "class_id": class_info.id
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{class_id}/status", response_model=dict)
async def update_class_status(
    class_id: int,
    status_data: ClassStatusUpdate,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """更新班级状态（关闭/开放）"""
    class_info = await ClassService.get_class_by_id(db, class_id)
    
    if not class_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="班级不存在"
        )
    
    # 权限检查：只能操作自己的班级
    if class_info.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能操作自己创建的班级"
        )
    
    try:
        class_info = await ClassService.update_class_status(db, class_info, status_data)
        status_text = "开放" if class_info.status else "关闭"
        return {
            "message": f"班级已{status_text}",
            "class_id": class_info.id,
            "status": class_info.status
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{class_id}", response_model=dict)
async def delete_class(
    class_id: int,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """删除班级（仅当无绑定学员时）"""
    class_info = await ClassService.get_class_by_id(db, class_id)
    
    if not class_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="班级不存在"
        )
    
    # 权限检查：只能删除自己的班级
    if class_info.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能删除自己创建的班级"
        )
    
    # 检查是否有学员
    student_count = await ClassService.get_class_student_count(db, class_id)
    if student_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"班级还有{student_count}个学员，无法删除"
        )
    
    # 删除班级
    await db.delete(class_info)
    await db.commit()
    
    logger.info(f"班级删除: {class_id}, 导师: {current_user.id}")
    
    return {
        "message": "班级删除成功",
        "class_id": class_id
    }


@router.get("/{class_id}/students", response_model=dict)
async def get_class_students(
    class_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取班级学生列表（包含成长值）"""
    from sqlalchemy import func, select, and_
    from app.models.class_student import ClassStudent, BindStatus
    from app.models.growth_log import Growth

    # 检查班级是否存在
    class_info = await ClassService.get_class_by_id(db, class_id)
    if not class_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="班级不存在"
        )

    # 权限检查：管理员可查看所有班级，导师只能查看自己的班级，班级助理只能查看被授权的班级
    from app.services.class_assistant_service import ClassAssistantService
    if current_user.role.role_name not in ["super_admin", "admin"]:
        # 检查是否是班级的创建者
        if class_info.teacher_id != current_user.id:
            # 检查是否是班级的助理
            is_assistant = await ClassAssistantService.is_assistant_of_class(db, current_user.id, class_id)
            if not is_assistant:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="无权限查看此班级"
                )

    # 查询班级学生，只显示已通过或未绑定（导师导入）且未删除且未停用的学员
    from sqlalchemy.orm import selectinload
    from app.models.class_student import BindStatus
    result = await db.execute(
        select(ClassStudent)
        .options(selectinload(ClassStudent.student_profile))
        .where(
            ClassStudent.class_id == class_id,
            ClassStudent.bind_status.in_([BindStatus.NONE.value, BindStatus.APPROVED.value, BindStatus.PENDING.value]),
            ClassStudent.is_deleted == False,
            ClassStudent.is_active == True
        )
    )
    class_students = result.scalars().all()
    
    students = []
    for cs in class_students:
            # 初始化变量
            user_id = None
            real_name = cs.name_in_class
            if not real_name or real_name == '??':
                # 如果没有班级内姓名，尝试使用学员档案的真实姓名
                if cs.student_profile and cs.student_profile.real_name:
                    real_name = cs.student_profile.real_name
                else:
                    # 跳过使用默认名称的学员，只显示实际添加的学员
                    continue
            available_score = 0
            
            # 如果有学生档案，获取用户ID
            if cs.student_profile:
                user_id = cs.student_profile.user_id
            else:
                # 如果没有学生档案，使用班级学生ID作为临时ID
                user_id = f"temp_{cs.id}"
            
            # 从Growth表计算成长值
            growth_log_result = await db.execute(
                select(func.sum(Growth.change_value)).where(
                    Growth.class_student_id == cs.id
                )
            )
            total_score = growth_log_result.scalar()
            available_score = float(total_score) if total_score else 0
            
            students.append({
                "id": user_id,
                "real_name": real_name,
                "name_in_class": cs.name_in_class,
                "student_no_in_class": cs.student_no_in_class,
                "bind_status": cs.bind_status,
                "created_at": cs.created_at,
                "available_score": available_score
            })
    
    return {
        "items": students,
        "total": len(students)
    }
