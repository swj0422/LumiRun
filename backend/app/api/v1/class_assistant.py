from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user, require_teacher
from app.services.class_assistant_service import ClassAssistantService
from app.models.user import User
from app.models.class_assistant import ClassAssistant
from app.models.class_info import ClassInfo
from app.core.logger import logger

router = APIRouter()


from pydantic import BaseModel


class AddAssistantRequest(BaseModel):
    class_id: int
    assistant_id: int
    assistant_email: str


@router.post("", response_model=dict)
async def add_assistant(
    request: AddAssistantRequest,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    """添加班级助理"""
    try:
        class_assistant = await ClassAssistantService.add_assistant(
            db=db,
            teacher_id=current_user.id,
            class_id=request.class_id,
            assistant_id=request.assistant_id,
            assistant_email=request.assistant_email
        )
        return {
            "message": "添加班级助理成功",
            "class_assistant_id": class_assistant.id
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


class RemoveAssistantRequest(BaseModel):
    class_id: int
    assistant_id: int


@router.delete("", response_model=dict)
async def remove_assistant(
    request: RemoveAssistantRequest,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    """移除班级助理"""
    try:
        await ClassAssistantService.remove_assistant(
            db=db,
            teacher_id=current_user.id,
            class_id=request.class_id,
            assistant_id=request.assistant_id
        )
        return {
            "message": "移除班级助理成功"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/class/{class_id}", response_model=dict)
async def get_class_assistants(
    class_id: int,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    """获取班级的助理列表"""
    from app.services.class_service import ClassService

    # 检查班级是否存在且属于该导师
    class_info = await ClassService.get_class_by_id(db, class_id)
    if not class_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="班级不存在"
        )

    if class_info.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限查看此班级的助理列表"
        )

    # 使用 selectinload 显式加载 assistant 关系
    result = await db.execute(
        select(ClassAssistant)
        .where(ClassAssistant.class_id == class_id)
        .options(selectinload(ClassAssistant.assistant))
        .order_by(ClassAssistant.created_at.desc())
    )
    assistants = result.scalars().all()

    assistant_list = []
    for assistant in assistants:
        assistant_list.append({
            "id": assistant.id,
            "assistant_id": assistant.assistant_id,
            "assistant_email": assistant.assistant_email,
            "assistant_name": assistant.assistant.real_name if assistant.assistant else "",
            "status": assistant.status,
            "created_at": assistant.created_at
        })

    return {
        "items": assistant_list
    }


@router.get("/user", response_model=dict)
async def get_user_assistant_classes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取用户作为助理的班级列表"""
    # 使用 selectinload 显式加载 teacher 关系
    result = await db.execute(
        select(ClassInfo)
        .join(ClassAssistant, ClassAssistant.class_id == ClassInfo.id)
        .where(
            ClassAssistant.assistant_id == current_user.id,
            ClassAssistant.status == True
        )
        .options(selectinload(ClassInfo.teacher))
        .order_by(ClassInfo.created_at.desc())
    )
    classes = result.scalars().all()

    class_list = []
    for cls in classes:
        class_list.append({
            "id": cls.id,
            "school_name": cls.school_name,
            "session": cls.session,
            "class_name": cls.class_name,
            "teacher_id": cls.teacher_id,
            "teacher_name": cls.teacher.real_name if cls.teacher else "",
            "status": cls.status,
            "created_at": cls.created_at
        })

    return {
        "items": class_list
    }


@router.get("/user/check", response_model=dict)
async def check_user_assistant_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """检查用户是否有班级助理授权记录"""
    # 检查是否存在有效的班级助理授权记录
    result = await db.execute(
        select(ClassAssistant)
        .where(
            ClassAssistant.assistant_id == current_user.id,
            ClassAssistant.status == True
        )
    )
    has_assistant_role = result.scalar_one_or_none() is not None

    return {
        "has_assistant_role": has_assistant_role
    }