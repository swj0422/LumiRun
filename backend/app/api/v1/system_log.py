from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_user, require_teacher, require_admin
from app.models.system_log import SystemLog, LogType, LogLevel
from app.models.user import User
from app.services.log_service import LogService
from pydantic import BaseModel, Field

router = APIRouter()


class LogQuery(BaseModel):
    log_type: Optional[LogType] = None
    log_level: Optional[LogLevel] = None
    module: Optional[str] = None
    action: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


@router.get("/")
async def get_logs(
    log_type: Optional[LogType] = Query(None),
    log_level: Optional[LogLevel] = Query(None),
    module: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    biz_type: Optional[str] = Query(None),
    biz_id: Optional[int] = Query(None),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取系统日志列表（管理员）"""
    logs, total = await LogService.get_logs(
        db=db,
        log_type=log_type,
        log_level=log_level,
        module=module,
        action=action,
        biz_type=biz_type,
        biz_id=biz_id,
        start_time=start_time,
        end_time=end_time,
        skip=skip,
        limit=limit
    )
    
    log_list = []
    for log in logs:
        log_list.append({
            "id": log.id,
            "user_id": log.user_id,
            "username": log.username,
            "real_name": log.real_name,
            "log_type": log.log_type,
            "log_level": log.log_level,
            "module": log.module,
            "action": log.action,
            "biz_type": log.biz_type,
            "biz_id": log.biz_id,
            "ip_address": log.ip_address,
            "request_url": log.request_url,
            "request_method": log.request_method,
            "response_status": log.response_status,
            "error_message": log.error_message,
            "created_at": log.created_at
        })
    
    return {
        "items": log_list,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/user")
async def get_user_logs(
    module: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    biz_type: Optional[str] = Query(None),
    biz_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户的系统日志"""
    logs, total = await LogService.get_logs(
        db=db,
        user_id=current_user.id,
        module=module,
        action=action,
        biz_type=biz_type,
        biz_id=biz_id,
        skip=skip,
        limit=limit
    )
    
    log_list = []
    for log in logs:
        log_list.append({
            "id": log.id,
            "log_type": log.log_type,
            "log_level": log.log_level,
            "module": log.module,
            "action": log.action,
            "biz_type": log.biz_type,
            "biz_id": log.biz_id,
            "ip_address": log.ip_address,
            "request_url": log.request_url,
            "request_method": log.request_method,
            "response_status": log.response_status,
            "error_message": log.error_message,
            "created_at": log.created_at
        })
    
    return {
        "items": log_list,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/error")
async def get_error_logs(
    biz_type: Optional[str] = Query(None),
    biz_id: Optional[int] = Query(None),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取错误日志（管理员）"""
    logs, total = await LogService.get_logs(
        db=db,
        log_level=LogLevel.ERROR,
        biz_type=biz_type,
        biz_id=biz_id,
        start_time=start_time,
        end_time=end_time,
        skip=skip,
        limit=limit
    )
    
    log_list = []
    for log in logs:
        log_list.append({
            "id": log.id,
            "user_id": log.user_id,
            "username": log.username,
            "real_name": log.real_name,
            "module": log.module,
            "action": log.action,
            "biz_type": log.biz_type,
            "biz_id": log.biz_id,
            "ip_address": log.ip_address,
            "request_url": log.request_url,
            "request_method": log.request_method,
            "response_status": log.response_status,
            "error_message": log.error_message,
            "created_at": log.created_at
        })
    
    return {
        "items": log_list,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/{log_id}")
async def get_log(
    log_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取系统日志详情（管理员）"""
    log = await LogService.get_log_by_id(db=db, log_id=log_id)
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="日志不存在"
        )
    
    return {
        "id": log.id,
        "user_id": log.user_id,
        "username": log.username,
        "real_name": log.real_name,
        "log_type": log.log_type,
        "log_level": log.log_level,
        "module": log.module,
        "action": log.action,
        "biz_type": log.biz_type,
        "biz_id": log.biz_id,
        "ip_address": log.ip_address,
        "user_agent": log.user_agent,
        "request_url": log.request_url,
        "request_method": log.request_method,
        "request_params": log.request_params,
        "response_status": log.response_status,
        "error_message": log.error_message,
        "created_at": log.created_at
    }
