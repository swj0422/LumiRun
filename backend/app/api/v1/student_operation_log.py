from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime
from app.core.database import get_db
from app.core.security import require_manager
from app.models.user import User
from app.models.student_operation_log import StudentOperationLog
from sqlalchemy import select, and_, or_

router = APIRouter()


@router.get("/")
async def get_student_operation_logs(
    class_id: Optional[int] = Query(None, description="班级 ID"),
    operation_type: Optional[str] = Query(None, description="操作类型：add/delete/unbind/tag_add/tag_delete/note_add/note_update"),
    student_name: Optional[str] = Query(None, description="学员姓名"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="每页记录数"),
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """获取学员操作日志列表"""
    # 构建查询
    query = select(StudentOperationLog)
    
    # 班级筛选 - 由于我们现在存储的是class_name，无法直接按class_id筛选
    # 如果需要按班级筛选，需要修改为按class_name模糊匹配
    
    # 操作类型筛选
    if operation_type:
        query = query.where(StudentOperationLog.operation_type == operation_type)
    
    # 学员姓名搜索
    if student_name:
        query = query.where(StudentOperationLog.student_name.like(f"%{student_name}%"))
    
    # 时间范围筛选
    if start_time:
        query = query.where(StudentOperationLog.created_at >= start_time)
    if end_time:
        query = query.where(StudentOperationLog.created_at <= end_time)
    
    # 计算总数
    count_query = select(StudentOperationLog.id)
    if operation_type:
        count_query = count_query.where(StudentOperationLog.operation_type == operation_type)
    if student_name:
        count_query = count_query.where(StudentOperationLog.student_name.like(f"%{student_name}%"))
    if start_time:
        count_query = count_query.where(StudentOperationLog.created_at >= start_time)
    if end_time:
        count_query = count_query.where(StudentOperationLog.created_at <= end_time)
    
    count_result = await db.execute(count_query)
    total = len(count_result.all())
    
    # 排序和分页
    query = query.order_by(StudentOperationLog.created_at.desc())
    query = query.offset(skip).limit(limit)
    
    # 执行查询
    result = await db.execute(query)
    logs = result.scalars().all()
    
    # 构建返回数据
    log_list = []
    for log in logs:
        log_list.append({
            "id": log.id,
            "operator_name": log.operator_name,
            "class_name": log.class_name,
            "student_name": log.student_name,
            "operation_type": log.operation_type,
            "operation_content": log.operation_content,
            "ip_address": log.ip_address,
            "created_at": log.created_at
        })
    
    return {
        "items": log_list,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/{log_id}")
async def get_student_operation_log_detail(
    log_id: int,
    current_user: User = Depends(require_manager),
    db: AsyncSession = Depends(get_db)
):
    """获取学员操作日志详情"""
    # 查询日志
    log = await db.get(StudentOperationLog, log_id)
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="日志不存在"
        )
    
    # 移除权限检查，因为我们不再存储operator_id字段
    
    return {
        "id": log.id,
        "operator_name": log.operator_name,
        "class_name": log.class_name,
        "student_name": log.student_name,
        "operation_type": log.operation_type,
        "operation_content": log.operation_content,
        "before_data": log.before_data,
        "after_data": log.after_data,
        "ip_address": log.ip_address,
        "created_at": log.created_at
    }
