from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base


class Wish(Base):
    """学员心愿表"""
    __tablename__ = "wish"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("sys_user.id"), nullable=False, comment="学员ID")
    gift_id = Column(Integer, ForeignKey("gift.id"), nullable=False, comment="礼品ID")
    class_id = Column(Integer, ForeignKey("class_info.id"), nullable=False, comment="班级ID")
    status = Column(Boolean, default=True, nullable=False, comment="心愿状态：0-已处理，1-未处理")
    notified_at = Column(DateTime, comment="通知时间")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="心愿创建时间")
    
    # 关系
    user = relationship("User", back_populates="user_wishes")
    gift = relationship("Gift", back_populates="gift_wishes")
    class_info = relationship("ClassInfo")
