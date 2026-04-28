from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class StudentBind(BaseModel):
    """学员绑定模型"""
    qr_code: str = Field(..., description="班级二维码")
    name_in_class: str = Field(..., max_length=50, description="班级内姓名（老师给的名字）")
    student_no_in_class: str = Field(..., description="班级内学号（老师给的学号）")


class StudentClassResponse(BaseModel):
    """学员绑定响应模型"""
    id: int
    student_profile_id: int
    name_in_class: str
    student_no_in_class: str
    class_id: int
    class_name: str
    school_name: str
    bind_time: datetime
    is_approved: bool
    
    class Config:
        from_attributes = True


class StudentSimpleResponse(BaseModel):
    """学员简要信息响应模型"""
    id: int
    name_in_class: str
    student_no_in_class: str
    class_id: int
    class_name: str
    school_name: str
    session: str
    available_score: int
    is_approved: bool
    tags: list = []
    
    class Config:
        from_attributes = True
