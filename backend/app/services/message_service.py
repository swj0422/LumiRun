from datetime import datetime
from typing import Optional, List
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.message import Message
from app.models.user import User
from app.core.logger import logger


class MessageService:
    """消息通知服务"""
    
    @staticmethod
    async def create_message(
        db: AsyncSession,
        user_id: int,
        content: str,
        message_type: int
    ) -> Message:
        """创建消息通知"""
        message = Message(
            user_id=user_id,
            content=content,
            type=message_type,
            is_read=False,
            created_at=datetime.utcnow()
        )
        
        db.add(message)
        await db.commit()
        await db.refresh(message)
        
        logger.info(f"创建消息通知: 用户ID {user_id}, 类型: {message_type}, 内容: {content}")
        return message
    
    @staticmethod
    async def get_user_messages(
        db: AsyncSession,
        user_id: int,
        is_read: Optional[bool] = None,
        message_type: Optional[int] = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[Message], int]:
        """获取用户的消息通知"""
        # 构建查询条件
        query = select(Message).where(Message.user_id == user_id)
        
        if is_read is not None:
            query = query.where(Message.is_read == is_read)
        if message_type is not None:
            query = query.where(Message.type == message_type)
        
        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar()
        
        # 获取分页数据
        query = query.order_by(Message.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        messages = result.scalars().all()
        
        return messages, total
    
    @staticmethod
    async def mark_message_as_read(
        db: AsyncSession,
        message_id: int,
        user_id: int
    ) -> Message:
        """标记消息为已读"""
        result = await db.execute(
            select(Message).where(
                Message.id == message_id,
                Message.user_id == user_id
            )
        )
        message = result.scalar_one_or_none()
        
        if not message:
            raise ValueError("消息不存在")
        
        message.is_read = True
        await db.commit()
        await db.refresh(message)
        
        logger.info(f"标记消息为已读: 消息ID {message_id}")
        return message
    
    @staticmethod
    async def mark_all_messages_as_read(
        db: AsyncSession,
        user_id: int,
        message_type: Optional[int] = None
    ) -> int:
        """标记所有消息为已读"""
        # 构建查询条件
        query = select(Message).where(
            Message.user_id == user_id,
            Message.is_read == False
        )
        
        if message_type is not None:
            query = query.where(Message.type == message_type)
        
        # 执行更新
        result = await db.execute(
            Message.__table__.update().where(
                Message.user_id == user_id,
                Message.is_read == False,
                Message.type == message_type if message_type else True
            ).values(is_read=True)
        )
        
        await db.commit()
        
        logger.info(f"标记所有消息为已读: 用户ID {user_id}, 类型: {message_type}, 数量: {result.rowcount}")
        return result.rowcount
    
    @staticmethod
    async def get_unread_message_count(
        db: AsyncSession,
        user_id: int,
        message_type: Optional[int] = None
    ) -> int:
        """获取未读消息数量"""
        # 构建查询条件
        query = select(func.count()).select_from(Message).where(
            Message.user_id == user_id,
            Message.is_read == False
        )
        
        if message_type is not None:
            query = query.where(Message.type == message_type)
        
        result = await db.execute(query)
        count = result.scalar()
        
        return count
    
    @staticmethod
    async def delete_message(
        db: AsyncSession,
        message_id: int,
        user_id: int
    ) -> bool:
        """删除消息"""
        result = await db.execute(
            Message.__table__.delete().where(
                Message.id == message_id,
                Message.user_id == user_id
            )
        )
        
        await db.commit()
        
        if result.rowcount > 0:
            logger.info(f"删除消息: 消息ID {message_id}")
            return True
        else:
            return False
    
    @staticmethod
    async def delete_all_messages(
        db: AsyncSession,
        user_id: int,
        message_type: Optional[int] = None
    ) -> int:
        """删除所有消息"""
        # 构建删除条件
        delete_condition = [
            Message.user_id == user_id
        ]
        
        if message_type is not None:
            delete_condition.append(Message.type == message_type)
        
        # 执行删除
        result = await db.execute(
            Message.__table__.delete().where(*delete_condition)
        )
        
        await db.commit()
        
        logger.info(f"删除所有消息: 用户ID {user_id}, 类型: {message_type}, 数量: {result.rowcount}")
        return result.rowcount
