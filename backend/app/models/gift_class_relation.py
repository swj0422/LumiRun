from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class GiftClassRelation(Base):
    """礼品-班级开放范围表"""
    __tablename__ = "gift_class_relation"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    gift_id = Column(Integer, ForeignKey("gift.id"), nullable=False, comment="礼品ID")
    class_id = Column(Integer, ForeignKey("class_info.id"), nullable=False, comment="班级ID")
    created_at = Column(DateTime, default=datetime.utcnow, comment="开放范围创建时间")
    
    # 关系
    gift = relationship("Gift", back_populates="class_relations")
    class_info = relationship("ClassInfo")
