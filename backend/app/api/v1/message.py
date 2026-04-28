from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.message import Message
from app.models.user import User
from app.services.message_service import MessageService
from pydantic import BaseModel, Field

router = APIRouter()


@router.get("/")
async def get_messages(
    is_read: Optional[bool] = Query(None),
    message_type: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取用户的消息通知"""
    messages, total = await MessageService.get_user_messages(
        db=db,
        user_id=current_user.id,
        is_read=is_read,
        message_type=message_type,
        skip=skip,
        limit=limit
    )
    
    message_list = []
    for message in messages:
        message_list.append({
            "id": message.id,
            "content": message.content,
            "type": message.type,
            "type_name": {
                1: "解绑通知",
                2: "礼品补货通知",
                3: "成长值变动通知",
                4: "订单状态通知"
            }.get(message.type, "其他通知"),
            "is_read": message.is_read,
            "created_at": message.created_at
        })
    
    return {
        "items": message_list,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/unread-count")
async def get_unread_message_count(
    message_type: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取未读消息数量"""
    count = await MessageService.get_unread_message_count(
        db=db,
        user_id=current_user.id,
        message_type=message_type
    )
    
    return {
        "unread_count": count
    }


@router.post("/{message_id}/read")
async def mark_message_as_read(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """标记消息为已读"""
    try:
        message = await MessageService.mark_message_as_read(
            db=db,
            message_id=message_id,
            user_id=current_user.id
        )
        
        return {
            "message": "标记成功",
            "message_id": message.id,
            "is_read": message.is_read
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/read-all")
async def mark_all_messages_as_read(
    message_type: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """标记所有消息为已读"""
    count = await MessageService.mark_all_messages_as_read(
        db=db,
        user_id=current_user.id,
        message_type=message_type
    )
    
    return {
        "message": "标记成功",
        "count": count
    }


@router.delete("/{message_id}")
async def delete_message(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除消息"""
    success = await MessageService.delete_message(
        db=db,
        message_id=message_id,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="消息不存在"
        )
    
    return {
        "message": "删除成功"
    }


@router.delete("/")
async def delete_all_messages(
    message_type: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除所有消息"""
    count = await MessageService.delete_all_messages(
        db=db,
        user_id=current_user.id,
        message_type=message_type
    )
    
    return {
        "message": "删除成功",
        "count": count
    }
