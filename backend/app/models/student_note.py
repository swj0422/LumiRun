from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class StudentNote(Base):
    """学员备注表"""
    __tablename__ = "student_note"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    class_student_id = Column(Integer, ForeignKey("class_student.id"), unique=True, nullable=False, comment="班级学员ID")
    real_name = Column(String(50), nullable=True, comment="真实姓名")
    learning_characteristics = Column(Text, nullable=True, comment="学习特点")
    personality_suggestions = Column(Text, nullable=True, comment="性格建议")
    performance_summary = Column(Text, nullable=True, comment="表现总结")
    tags = Column(Text, nullable=True, comment="标签JSON")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关系
    class_student = relationship("ClassStudent", back_populates="note")
