from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class GiftBase(BaseModel):
    """礼品基础模型"""
    name: str = Field(..., max_length=100, description="礼品名称")
    description: Optional[str] = Field(None, description="礼品描述")
    cost_score: int = Field(..., ge=0, description="兑换所需成长值")
    stock: int = Field(..., ge=0, description="礼品库存")


class GiftCreate(GiftBase):
    """礼品创建模型"""
    pass


class GiftUpdate(BaseModel):
    """礼品更新模型"""
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    cost_score: Optional[int] = Field(None, ge=0)
    stock: Optional[int] = Field(None, ge=0)
    status: Optional[int] = None


class GiftStatusUpdate(BaseModel):
    """礼品状态更新模型"""
    status: bool = Field(..., description="礼品状态：0-下架，1-上架")


class GiftStockUpdate(BaseModel):
    """礼品库存更新模型"""
    add_stock: int = Field(..., gt=0, description="补货数量")
    notify_wishers: bool = Field(default=False, description="是否通知心愿学员")


class GiftResponse(GiftBase):
    """礼品响应模型"""
    id: int
    image_url: Optional[str]
    status: bool
    status_name: str
    teacher_id: int
    teacher_name: str
    current_stock: int
    total_in_stock: int
    total_out_stock: int
    class_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class GiftDetailResponse(GiftResponse):
    """礼品详情响应模型"""
    class_ids: List[int]
    class_names: List[str]


class GiftSimpleResponse(BaseModel):
    """礼品简要响应模型"""
    id: int
    name: str
    cost_score: int
    current_stock: int
    image_url: Optional[str]
    
    class Config:
        from_attributes = True


class GiftClassCreate(BaseModel):
    """礼品班级关联创建模型"""
    gift_id: int
    class_id: int
