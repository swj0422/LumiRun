from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base


class GrowthOperationLog(Base):
    """成长值操作日志表（不可变记录）"""
    __tablename__ = "growth_operation_log"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_name = Column(String(100), nullable=False, comment="学员姓名")
    class_name = Column(String(100), nullable=False, comment="班级名称")
    teacher_name = Column(String(100), nullable=False, comment="导师姓名")
    operator_name = Column(String(100), nullable=False, comment="操作人姓名")
    old_value = Column(Integer, nullable=False, comment="修改前的成长值")
    new_value = Column(Integer, nullable=False, comment="修改后的成长值")
    change_value = Column(Integer, nullable=False, comment="成长值变动值")
    reason = Column(Text, nullable=False, comment="变动原因")
    operation_type = Column(String(20), nullable=False, comment="操作类型：add, update, delete")
    created_at = Column(DateTime, default=datetime.utcnow, comment="记录时间")
