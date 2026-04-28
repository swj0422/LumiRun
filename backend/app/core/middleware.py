from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
from app.core.logger import logger
from app.models.system_log import SystemLog, LogType, LogLevel
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal


class PerformanceMonitorMiddleware(BaseHTTPMiddleware):
    """接口性能监控中间件"""
    
    async def dispatch(self, request: Request, call_next):
        # 记录请求开始时间
        start_time = time.time()
        
        # 处理请求
        response = await call_next(request)
        
        # 计算响应时间
        process_time = time.time() - start_time
        
        # 记录性能日志
        await self.log_performance(request, response, process_time)
        
        # 添加响应时间到响应头
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
    
    async def log_performance(self, request: Request, response: Response, process_time: float):
        """记录性能日志"""
        # 排除静态文件和健康检查等不需要监控的路径
        path = request.url.path
        if path.startswith("/static") or path == "/health":
            return
        
        # 记录性能信息
        logger.info(
            f"API Performance: {request.method} {path} "
            f"status={response.status_code} "
            f"time={process_time:.4f}s"
        )
        
        # 异步记录到数据库
        try:
            async with AsyncSessionLocal() as db:
                # 提取用户信息（如果有）
                user_id = None
                username = ""
                real_name = ""
                
                # 从请求中获取用户信息（如果在中间件中可以获取到）
                # 这里需要根据实际的认证中间件实现来调整
                if hasattr(request.state, "user") and request.state.user:
                    user = request.state.user
                    user_id = user.id
                    username = user.username
                    real_name = user.real_name
                
                # 创建系统日志记录
                system_log = SystemLog(
                    user_id=user_id,
                    username=username,
                    real_name=real_name,
                    log_type=LogType.OTHER,
                    log_level=LogLevel.INFO,
                    module="性能监控",
                    action="API调用",
                    request_params=f'{"method": "{request.method}", "path": "{path}", "query": "{dict(request.query_params)}"}',
                    response_status=response.status_code,
                    ip_address=request.client.host if request.client else ""
                )
                
                db.add(system_log)
                await db.commit()
        except Exception as e:
            # 记录性能日志失败时不影响主流程
            logger.error(f"记录性能日志失败: {e}")


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """错误处理中间件"""
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            # 记录详细的错误信息
            import traceback
            error_message = str(e)
            error_traceback = traceback.format_exc()
            
            # 构建错误日志
            error_log = {
                "request_path": str(request.url),
                "request_method": request.method,
                "client_ip": request.client.host if request.client else "unknown",
                "error_type": type(e).__name__,
                "error_message": error_message,
                "traceback": error_traceback
            }
            
            # 记录到日志文件
            logger.error(f"Global error: {error_message}", exc_info=True)
            
            # 异步记录到数据库
            try:
                async with AsyncSessionLocal() as db:
                    # 提取用户信息（如果有）
                    user_id = None
                    username = ""
                    real_name = ""
                    
                    # 从请求中获取用户信息（如果在中间件中可以获取到）
                    if hasattr(request.state, "user") and request.state.user:
                        user = request.state.user
                        user_id = user.id
                        username = user.username
                        real_name = user.real_name
                    
                    # 创建系统日志记录
                    system_log = SystemLog(
                        user_id=user_id,
                        username=username,
                        real_name=real_name,
                        log_type=LogType.ERROR,
                        log_level=LogLevel.ERROR,
                        module="错误监控",
                        action="系统错误",
                        request_params=f'{"method": "{request.method}", "path": "{request.url.path}"}',
                        error_message=error_message,
                        ip_address=request.client.host if request.client else ""
                    )
                    
                    db.add(system_log)
                    await db.commit()
            except Exception as log_error:
                # 记录错误日志失败时不影响主流程
                logger.error(f"记录错误日志失败: {log_error}")
            
            # 这里可以根据需要返回自定义错误响应
            # 暂时直接抛出，让FastAPI的默认错误处理机制处理
            raise
