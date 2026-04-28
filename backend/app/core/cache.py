import json
import redis.asyncio as redis
from typing import Optional, Any, Union
from app.core.config import get_settings

settings = get_settings()

# Redis连接池
redis_pool = redis.ConnectionPool.from_url(
    settings.REDIS_URL,
    max_connections=settings.REDIS_POOL_SIZE,
    decode_responses=True
)


class CacheManager:
    """缓存管理器"""
    
    def __init__(self):
        self.redis = redis.Redis(connection_pool=redis_pool)
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        value = await self.redis.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None
    
    async def set(
        self,
        key: str,
        value: Any,
        expire: int = None
    ) -> bool:
        """设置缓存"""
        if expire is None:
            expire = settings.CACHE_EXPIRE_SECONDS
        
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        
        return await self.redis.setex(key, expire, value)
    
    async def delete(self, key: str) -> bool:
        """删除缓存"""
        return await self.redis.delete(key) > 0
    
    async def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        return await self.redis.exists(key) > 0
    
    async def clear_pattern(self, pattern: str) -> int:
        """清除匹配模式的缓存"""
        keys = await self.redis.keys(pattern)
        if keys:
            return await self.redis.delete(*keys)
        return 0
    
    async def close(self):
        """关闭连接"""
        await self.redis.close()


# 全局缓存管理器实例
cache = CacheManager()


# 装饰器：缓存结果
def cache_result(expire: int = None, key_prefix: str = ""):
    """缓存函数结果的装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # 尝试从缓存获取
            cached_value = await cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 缓存结果
            await cache.set(cache_key, result, expire)
            
            return result
        return wrapper
    return decorator
