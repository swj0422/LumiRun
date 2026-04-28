from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class OrderCreate(BaseModel):
    """订单创建模型"""
    gift_id: int = Field(..., description="礼品ID")


class OrderCancel(BaseModel):
    """订单取消模型"""
    reason: str = Field(..., max_length=255, description="取消原因")


class OrderVerify(BaseModel):
    """订单核销模型"""
    qr_code: str = Field(..., description="订单核销二维码")


class OrderResponse(BaseModel):
    """订单响应模型"""
    id: int
    user_id: int
    student_name: str
    student_phone: str
    gift_id: int
    gift_name: str
    class_id: int
    class_name: str
    teacher_id: int
    teacher_name: str
    cost_score: int
    status: int
    status_name: str
    qr_code: str
    cancel_reason: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class OrderDetailResponse(OrderResponse):
    """订单详情响应模型"""
    verify_time: Optional[datetime]
    verify_user_name: Optional[str]
