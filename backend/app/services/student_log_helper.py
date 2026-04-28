from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request
from app.services.log_service import LogService
from app.services.student_operation_log_service import StudentOperationLogService
from app.models.system_log import LogType, LogLevel
from app.core.logger import logger


async def log_system_operation(
    db: AsyncSession,
    request: Request,
    user_id: int,
    action: str,
    biz_id: int,
    request_params: Optional[Dict[str, Any]] = None,
    response_status: int = 200
) -> None:
    """
    记录系统操作日志
    
    Args:
        db: 数据库会话
        request: FastAPI 请求对象
        user_id: 用户ID
        action: 操作动作（如"停用学员"、"解绑学员"等）
        biz_id: 业务ID
        request_params: 请求参数
        response_status: 响应状态码
    """
    try:
        await LogService.create_log(
            db=db,
            user_id=user_id,
            log_type=LogType.OPERATION,
            log_level=LogLevel.INFO,
            module="学员管理",
            action=action,
            biz_type="student",
            biz_id=biz_id,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            request_url=str(request.url),
            request_method=request.method,
            request_params=request_params,
            response_status=response_status
        )
    except Exception as log_error:
        logger.error(f"记录系统操作日志失败: {str(log_error)}")


async def log_student_operation(
    db: AsyncSession,
    user_id: int,
    user_name: str,
    student_info: Dict[str, Any],
    operation_type: str,
    operation_content: str,
    before_data: Optional[Dict[str, Any]] = None,
    after_data: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None
) -> None:
    """
    记录学员操作日志
    
    Args:
        db: 数据库会话
        user_id: 操作用户ID
        user_name: 操作用户姓名
        student_info: 学员信息字典，包含 class_id, id, name_in_class, student_no_in_class
        operation_type: 操作类型（如"stop"、"unbind"、"update_info"、"restore"等）
        operation_content: 操作内容描述
        before_data: 操作前数据
        after_data: 操作后数据
        ip_address: IP地址
    """
    try:
        await StudentOperationLogService.create_operation_log(
            db=db,
            operator_id=user_id,
            operator_name=user_name,
            class_id=student_info['class_id'],
            class_student_id=student_info['id'],
            student_name=student_info['name_in_class'],
            operation_type=operation_type,
            operation_content=operation_content,
            before_data=before_data,
            after_data=after_data,
            ip_address=ip_address
        )
    except Exception as log_error:
        logger.error(f"记录学员操作日志失败: {str(log_error)}")
