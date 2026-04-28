from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class VerifyRecord(Base):
    """核销记录表"""
    __tablename__ = "verify_record"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("gift_order.id"), unique=True, nullable=False, comment="订单ID")
    verify_user_id = Column(Integer, ForeignKey("sys_user.id"), nullable=False, comment="核销导师ID")
    verify_time = Column(DateTime, default=datetime.utcnow, comment="核销时间")
    class_id = Column(Integer, ForeignKey("class_info.id"), nullable=False, comment="班级ID")
    
    # 关系
    order = relationship("GiftOrder", back_populates="verify_record")
    verify_user = relationship("User")
    class_info = relationship("ClassInfo", back_populates="verify_records")
