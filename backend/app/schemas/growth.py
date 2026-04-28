from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class GrowthLogCreate(BaseModel):
    """成长值录入模型"""
    student_name: str = Field(..., description="学员姓名（支持模糊匹配）")
    student_no: Optional[str] = Field(None, description="学员学号")
    class_id: int = Field(..., description="班级ID")
    change_score: int = Field(..., description="成长值变动值（正数加分，负数减分）")
    reason: str = Field(..., description="变动原因")
    input_type: int = Field(default=1, description="录入方式：1-手动录入，2-语音录入")


class GrowthLogResponse(BaseModel):
    """成长值流水响应模型"""
    id: int
    user_id: int
    student_name: str
    class_id: int
    class_name: str
    teacher_id: int
    teacher_name: str
    change_score: int
    reason: str
    input_type: int
    input_type_name: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class GrowthScoreResponse(BaseModel):
    """成长值总额响应模型"""
    user_id: int
    student_name: str
    total_score: int
    available_score: int
    
    class Config:
        from_attributes = True


class GrowthReasonCreate(BaseModel):
    """成长值原因创建模型"""
    reason: str = Field(..., description="变动原因")


class GrowthReasonResponse(BaseModel):
    """成长值原因响应模型"""
    id: int
    reason: str
    created_at: datetime
    
    class Config:
        from_attributes = True
