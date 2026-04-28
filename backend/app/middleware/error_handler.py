from fastapi import Request, status
from fastapi.responses import JSONResponse
import traceback
import logging
from datetime import datetime

logger = logging.getLogger("lumirun")


async def error_handler(request: Request, exc: Exception):
    """全局错误处理中间件"""
    # 记录详细的错误信息
    error_message = str(exc)
    error_traceback = traceback.format_exc()
    
    # 构建错误日志
    error_log = {
        "timestamp": datetime.utcnow().isoformat(),
        "request_path": str(request.url),
        "request_method": request.method,
        "client_ip": request.client.host if request.client else "unknown",
        "error_type": type(exc).__name__,
        "error_message": error_message,
        "traceback": error_traceback
    }
    
    # 记录到日志文件
    logger.error(f"Global error: {error_message}", exc_info=True)
    
    # 根据错误类型返回不同的状态码
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    # 构建统一的错误响应
    error_response = {
        "error": {
            "code": status_code,
            "message": "服务器内部错误",
            "details": error_message
        }
    }
    
    # 在生产环境中，不返回详细的错误信息给客户端
    # 但在开发环境中可以返回更详细的信息
    import os
    if os.getenv("ENVIRONMENT") == "development":
        error_response["error"]["traceback"] = error_traceback
    
    return JSONResponse(
        status_code=status_code,
        content=error_response
    )


async def http_exception_handler(request: Request, exc):
    """HTTP异常处理"""
    # 记录HTTP异常
    logger.error(f"HTTP error: {exc.detail} (status: {exc.status_code})", exc_info=True)
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail
            }
        }
    )
