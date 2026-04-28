from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class ClassAssistant(Base):
    """班级助理表"""
    __tablename__ = "class_assistant"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    teacher_id = Column(Integer, ForeignKey("sys_user.id"), nullable=False, comment="授权导师ID")
    class_id = Column(Integer, ForeignKey("class_info.id"), nullable=False, comment="班级ID")
    assistant_id = Column(Integer, ForeignKey("sys_user.id"), nullable=False, comment="被授权为助理的用户ID")
    assistant_email = Column(String(100), nullable=False, comment="授权时填写的邮箱")
    status = Column(Boolean, default=True, nullable=False, comment="状态：1=启用 0=禁用")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 唯一约束：同一班级不可重复授权同一用户
    __table_args__ = (
        UniqueConstraint('class_id', 'assistant_id', name='unique_class_assistant'),
    )
    
    # 关系
    teacher = relationship("User", foreign_keys=[teacher_id], backref="class_assistants_as_teacher")
    assistant = relationship("User", foreign_keys=[assistant_id], backref="class_assistants_as_assistant")
    class_info = relationship("ClassInfo", backref="class_assistants")
