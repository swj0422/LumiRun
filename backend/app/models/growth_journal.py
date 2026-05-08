from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class GrowthOperationLog(Base):
    """成长操作日志表（不可变记录）"""
    __tablename__ = "growth_operation_log"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    class_student_id = Column(Integer, ForeignKey("class_student.id"), nullable=False, comment="班级学员ID")
    class_id = Column(Integer, ForeignKey("class_info.id"), nullable=False, comment="班级ID")
    change_value = Column(Integer, nullable=False, comment="成长值变动值")
    reason = Column(Text, nullable=False, comment="变动原因")
    operator_id = Column(Integer, ForeignKey("sys_user.id"), nullable=False, comment="操作导师ID")
    operator_name = Column(String(50), nullable=False, comment="操作导师姓名")
    input_type = Column(Integer, nullable=False, comment="录入方式：1-手动，2-语音，3-批量，4-系统")
    operation_type = Column(String(20), nullable=False, comment="操作类型：add/delete/update")
    created_at = Column(DateTime, default=datetime.utcnow, comment="操作时间")
