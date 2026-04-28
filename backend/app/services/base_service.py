from typing import List, Optional, Dict, Any, Type, TypeVar, Generic
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update, func
from sqlalchemy.orm import selectinload
from app.core.logger import logger

ModelType = TypeVar('ModelType')


class BaseService(Generic[ModelType]):
    """基础服务类，提供通用的CRUD操作"""
    
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    async def get_by_id(self, db: AsyncSession, id: int) -> Optional[ModelType]:
        """根据ID获取单个对象"""
        try:
            result = await db.execute(select(self.model).where(self.model.id == id))
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"获取{self.model.__name__}失败: {e}")
            return None
    
    async def get_all(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """获取所有对象"""
        try:
            result = await db.execute(select(self.model).offset(skip).limit(limit))
            return result.scalars().all()
        except Exception as e:
            logger.error(f"获取{self.model.__name__}列表失败: {e}")
            return []
    
    async def create(self, db: AsyncSession, **kwargs) -> Optional[ModelType]:
        """创建对象"""
        try:
            instance = self.model(**kwargs)
            db.add(instance)
            await db.commit()
            await db.refresh(instance)
            return instance
        except Exception as e:
            logger.error(f"创建{self.model.__name__}失败: {e}")
            await db.rollback()
            return None
    
    async def update(self, db: AsyncSession, id: int, **kwargs) -> Optional[ModelType]:
        """更新对象"""
        try:
            instance = await self.get_by_id(db, id)
            if not instance:
                return None
            
            for key, value in kwargs.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            
            await db.commit()
            await db.refresh(instance)
            return instance
        except Exception as e:
            logger.error(f"更新{self.model.__name__}失败: {e}")
            await db.rollback()
            return None
    
    async def delete(self, db: AsyncSession, id: int) -> bool:
        """删除对象"""
        try:
            result = await db.execute(delete(self.model).where(self.model.id == id))
            await db.commit()
            return result.rowcount > 0
        except Exception as e:
            logger.error(f"删除{self.model.__name__}失败: {e}")
            await db.rollback()
            return False
    
    async def get_count(self, db: AsyncSession, **filters) -> int:
        """获取对象数量"""
        try:
            query = select(self.model)
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.where(getattr(self.model, key) == value)
            
            result = await db.execute(select(func.count()).select_from(query.subquery()))
            return result.scalar() or 0
        except Exception as e:
            logger.error(f"获取{self.model.__name__}数量失败: {e}")
            return 0



