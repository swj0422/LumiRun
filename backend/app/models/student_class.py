from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Boolean, String
from sqlalchemy.orm import relationship
from app.core.database import Base


class StudentClass(Base):
    """学员-班级绑定表"""
    __tablename__ = "student_class"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    class_id = Column(Integer, ForeignKey("class_info.id"), nullable=False, comment="班级ID")
    student_no = Column(String(50), nullable=True, comment="学号")
    real_name = Column(String(50), nullable=False, comment="姓名")
    user_id = Column(Integer, ForeignKey("sys_user.id"), nullable=True, comment="学员ID")
    bind_time = Column(DateTime, comment="绑定时间")
    status = Column(Boolean, default=True, comment="绑定状态：0-已解绑，1-正常绑定")
    unbind_time = Column(DateTime, comment="解绑时间")
    unbind_operator_id = Column(Integer, ForeignKey("sys_user.id"), comment="解绑操作人ID")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关系
    student = relationship("User", back_populates="student_bindings", foreign_keys=[user_id])
    class_info = relationship("ClassInfo", back_populates="student_bindings")
    unbind_operator = relationship("User", foreign_keys=[unbind_operator_id])
