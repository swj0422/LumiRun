from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ClassBase(BaseModel):
    """班级基础模型"""
    school_name: str = Field(..., max_length=100, description="学校名称")
    session: str = Field(..., max_length=50, description="级")
    class_name: str = Field(..., max_length=50, description="班级名称")
    description: Optional[str] = Field(None, max_length=500, description="班级描述")


class ClassCreate(ClassBase):
    """班级创建模型"""
    pass


class ClassUpdate(BaseModel):
    """班级更新模型"""
    class_name: Optional[str] = Field(None, max_length=50)
    session: Optional[str] = Field(None, max_length=50, description="级")


class ClassStatusUpdate(BaseModel):
    """班级状态更新模型"""
    status: bool = Field(..., description="班级状态：0-关闭，1-开放")


class ClassResponse(ClassBase):
    """班级响应模型"""
    id: int
    teacher_id: int
    teacher_name: str
    status: bool
    qr_code: str
    qr_url: Optional[str]
    student_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
