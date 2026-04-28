from datetime import datetime, timedelta
from typing import Dict, Any
from fastapi import Request, HTTPException, status
import asyncio


class RateLimiter:
    """简单的接口限流中间件"""
    
    def __init__(self):
        # 存储请求记录: {key: (count, reset_time)}
        self.requests: Dict[str, tuple[int, datetime]] = {}
        # 默认限制：每分钟60次请求
        self.default_limit = 60
        self.default_window = 60  # 秒
    
    async def __call__(self, request: Request, limit: int = None, window: int = None):
        """限制请求频率"""
        # 生成限流键，可以按IP或用户ID
        client_ip = request.client.host if request.client else "unknown"
        user_id = None
        
        # 尝试从请求中获取用户信息
        if hasattr(request.state, "user") and request.state.user:
            user_id = request.state.user.id
        
        # 优先使用用户ID作为键，否则使用IP
        key = f"user:{user_id}" if user_id else f"ip:{client_ip}"
        
        # 使用默认值或传入的值
        current_limit = limit or self.default_limit
        current_window = window or self.default_window
        
        # 检查并更新请求记录
        now = datetime.utcnow()
        
        if key in self.requests:
            count, reset_time = self.requests[key]
            
            # 如果在时间窗口内
            if now < reset_time:
                # 检查是否超过限制
                if count >= current_limit:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="请求过于频繁，请稍后再试"
                    )
                # 更新计数
                self.requests[key] = (count + 1, reset_time)
            else:
                # 时间窗口已过，重置
                self.requests[key] = (1, now + timedelta(seconds=current_window))
        else:
            # 第一次请求，初始化记录
            self.requests[key] = (1, now + timedelta(seconds=current_window))
        
        # 清理过期记录
        await self._cleanup_expired()
    
    async def _cleanup_expired(self):
        """清理过期的请求记录"""
        now = datetime.utcnow()
        expired_keys = [
            key for key, (_, reset_time) in self.requests.items()
            if now >= reset_time
        ]
        for key in expired_keys:
            del self.requests[key]


# 创建全局限流器实例
rate_limiter = RateLimiter()


def require_rate_limit(limit: int = 60, window: int = 60):
    """请求限流依赖"""
    async def limiter(request: Request):
        await rate_limiter(request, limit=limit, window=window)
    return limiter
