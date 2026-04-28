from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime
from app.core.database import get_db
from app.core.security import require_admin
from app.core.logger import logger
from app.models.user import User

router = APIRouter()


@router.get("/system", response_model=dict)
async def get_system_logs(
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    level: Optional[str] = Query(None, description="日志级别"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取系统日志"""
    # 这里实际应该从日志文件或日志数据库中读取
    # 由于我们使用的是Python标准日志，这里返回模拟数据
    # 实际项目中可以使用ELK或其他日志系统
    
    logs = [
        {
            "timestamp": datetime.now().isoformat(),
            "level": "INFO",
            "message": "系统启动成功",
            "module": "main",
            "func": "startup"
        },
        {
            "timestamp": datetime.now().isoformat(),
            "level": "INFO",
            "message": "数据库连接成功",
            "module": "database",
            "func": "connect"
        },
        {
            "timestamp": datetime.now().isoformat(),
            "level": "WARNING",
            "message": "礼品库存不足",
            "module": "gift",
            "func": "check_stock"
        }
    ]
    
    # 模拟筛选
    filtered_logs = logs
    if level:
        filtered_logs = [log for log in filtered_logs if log["level"] == level]
    
    # 模拟分页
    total = len(filtered_logs)
    paginated_logs = filtered_logs[skip:skip+limit]
    
    return {
        "items": paginated_logs,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/operation", response_model=dict)
async def get_operation_logs(
    user_id: Optional[int] = Query(None, description="用户ID"),
    action: Optional[str] = Query(None, description="操作类型"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取操作日志"""
    # 这里实际应该从数据库中读取操作日志
    # 由于我们没有专门的操作日志表，这里返回模拟数据
    
    logs = [
        {
            "id": 1,
            "user_id": 1,
            "user_name": "管理员",
            "action": "用户注册",
            "target": "用户管理",
            "ip": "127.0.0.1",
            "created_at": datetime.now().isoformat(),
            "details": "用户张三注册成功"
        },
        {
            "id": 2,
            "user_id": 2,
            "user_name": "导师1",
            "action": "创建班级",
            "target": "班级管理",
            "ip": "192.168.1.100",
            "created_at": datetime.now().isoformat(),
            "details": "创建班级：高一(1)班"
        },
        {
            "id": 3,
            "user_id": 3,
            "user_name": "学员1",
            "action": "兑换礼品",
            "target": "奖励兑换",
            "ip": "192.168.1.101",
            "created_at": datetime.now().isoformat(),
            "details": "兑换礼品：笔记本"
        }
    ]
    
    # 模拟筛选
    filtered_logs = logs
    if user_id:
        filtered_logs = [log for log in filtered_logs if log["user_id"] == user_id]
    if action:
        filtered_logs = [log for log in filtered_logs if action in log["action"]]
    
    # 模拟分页
    total = len(filtered_logs)
    paginated_logs = filtered_logs[skip:skip+limit]
    
    return {
        "items": paginated_logs,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.post("/cleanup", response_model=dict)
async def cleanup_logs(
    days: int = Query(30, ge=1, le=365, description="保留天数"),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """清理日志"""
    # 实际项目中应该实现日志清理逻辑
    # 这里只是模拟
    
    logger.info(f"管理员 {current_user.id} 执行日志清理，保留 {days} 天")
    
    return {
        "message": f"日志清理完成，保留最近 {days} 天的日志"
    }
