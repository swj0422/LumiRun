from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


def utc_now():
    """获取当前UTC时间"""
    return datetime.utcnow()


class StudentOperationLog(Base):
    """学员操作日志表"""
    __tablename__ = "student_operation_log"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="日志 ID")
    operator_id = Column(Integer, nullable=False, comment="操作人ID")
    operator_name = Column(String(50), nullable=False, comment="操作人姓名")
    class_id = Column(Integer, nullable=False, comment="班级ID")
    class_student_id = Column(Integer, nullable=False, comment="学员ID")
    class_name = Column(String(100), nullable=False, comment="班级名称")
    student_name = Column(String(50), nullable=False, comment="学员姓名")
    operation_type = Column(String(20), nullable=False, index=True, comment="操作类型：add/delete/unbind/tag_add/tag_delete/note_add/note_update/update_info/restore")
    operation_content = Column(Text, nullable=False, comment="操作内容")
    before_data = Column(Text, nullable=True, comment="操作前数据（JSON）")
    after_data = Column(Text, nullable=True, comment="操作后数据（JSON）")
    ip_address = Column(String(50), nullable=True, comment="操作 IP")
    created_at = Column(DateTime, default=utc_now, nullable=False, comment="操作时间")
