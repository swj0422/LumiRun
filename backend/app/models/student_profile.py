from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime


class StudentProfile(Base):
    """学员档案表"""
    __tablename__ = "student_profile"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("sys_user.id"), unique=True, nullable=False)
    real_name = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="student_profile")
    class_students = relationship("ClassStudent", back_populates="student_profile")
