from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Boolean, String, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class Wish(Base):
    """学员心愿表"""
    __tablename__ = "wish"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("sys_user.id"), nullable=False, comment="学员ID")
    class_id = Column(Integer, ForeignKey("class_info.id"), nullable=False, comment="班级ID")
    title = Column(String(100), nullable=False, comment="心愿标题")
    description = Column(Text, comment="心愿描述")
    image_urls = Column(String(500), comment="图片URL，逗号分隔，最多3张")
    status = Column(Integer, default=0, nullable=False, comment="心愿状态：0-待处理，1-已实现，2-已拒绝")
    teacher_comment = Column(Text, comment="导师回复")
    created_at = Column(DateTime, default=datetime.now, nullable=False, comment="心愿创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="心愿更新时间")
    
    # 关系
    user = relationship("User", back_populates="user_wishes")
    class_info = relationship("ClassInfo")