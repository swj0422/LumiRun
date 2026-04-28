from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.system_log import SystemLog, LogType, LogLevel
from app.models.user import User
from app.core.logger import logger


class LogService:
    """系统日志服务"""
    
    @staticmethod
    async def create_log(
        db: AsyncSession,
        user_id: Optional[int] = None,
        log_type: LogType = LogType.OTHER,
        log_level: LogLevel = LogLevel.INFO,
        module: str = "unknown",
        action: str = "unknown",
        biz_type: Optional[str] = None,
        biz_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_url: Optional[str] = None,
        request_method: Optional[str] = None,
        request_params: Optional[Dict[str, Any]] = None,
        response_status: Optional[int] = None,
        error_message: Optional[str] = None
    ) -> SystemLog:
        """创建系统日志"""
        # 获取用户信息
        username = None
        real_name = None
        if user_id:
            user = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = user.scalar_one_or_none()
            if user:
                username = user.username
                real_name = user.real_name
        
        # 创建日志记录
        log = SystemLog(
            user_id=user_id,
            username=username,
            real_name=real_name,
            log_type=log_type,
            log_level=log_level,
            module=module,
            action=action,
            biz_type=biz_type,
            biz_id=biz_id,
            ip_address=ip_address,
            user_agent=user_agent,
            request_url=request_url,
            request_method=request_method,
            request_params=str(request_params) if request_params else None,
            response_status=response_status,
            error_message=error_message,
            created_at=datetime.utcnow()
        )
        
        db.add(log)
        await db.commit()
        await db.refresh(log)
        
        return log
    
    @staticmethod
    async def get_logs(
        db: AsyncSession,
        user_id: Optional[int] = None,
        log_type: Optional[LogType] = None,
        log_level: Optional[LogLevel] = None,
        module: Optional[str] = None,
        action: Optional[str] = None,
        biz_type: Optional[str] = None,
        biz_id: Optional[int] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[SystemLog], int]:
        """获取系统日志列表"""
        # 构建查询条件
        query = select(SystemLog)
        
        if user_id:
            query = query.where(SystemLog.user_id == user_id)
        if log_type:
            query = query.where(SystemLog.log_type == log_type)
        if log_level:
            query = query.where(SystemLog.log_level == log_level)
        if module:
            query = query.where(SystemLog.module == module)
        if action:
            query = query.where(SystemLog.action == action)
        if biz_type:
            query = query.where(SystemLog.biz_type == biz_type)
        if biz_id:
            query = query.where(SystemLog.biz_id == biz_id)
        if start_time:
            query = query.where(SystemLog.created_at >= start_time)
        if end_time:
            query = query.where(SystemLog.created_at <= end_time)
        
        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar()
        
        # 获取分页数据
        query = query.order_by(SystemLog.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        logs = result.scalars().all()
        
        return logs, total
    
    @staticmethod
    async def get_log_by_id(db: AsyncSession, log_id: int) -> Optional[SystemLog]:
        """根据ID获取系统日志"""
        result = await db.execute(
            select(SystemLog).where(SystemLog.id == log_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_logs(
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[SystemLog], int]:
        """获取指定用户的系统日志"""
        return await LogService.get_logs(
            db=db,
            user_id=user_id,
            skip=skip,
            limit=limit
        )
    
    @staticmethod
    async def get_error_logs(
        db: AsyncSession,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[SystemLog], int]:
        """获取错误日志"""
        return await LogService.get_logs(
            db=db,
            log_level=LogLevel.ERROR,
            start_time=start_time,
            end_time=end_time,
            skip=skip,
            limit=limit
        )
