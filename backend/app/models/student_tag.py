from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class StudentTag(Base):
    """学员标签关联表"""
    __tablename__ = "student_tag"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    class_student_id = Column(Integer, ForeignKey("class_student.id"), nullable=False, comment="班级学员ID")
    tag_id = Column(Integer, ForeignKey("tag.id"), nullable=False, comment="标签ID")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    
    __table_args__ = (
        UniqueConstraint('class_student_id', 'tag_id', name='uq_student_tag'),
    )
