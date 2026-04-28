from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class MessageResponse(BaseModel):
    """消息响应模型"""
    id: int
    user_id: int
    content: str
    type: int
    type_name: str
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class MessageDetailResponse(MessageResponse):
    """消息详情响应模型"""
    user_name: str
    user_phone: str