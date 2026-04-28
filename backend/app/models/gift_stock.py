from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class GiftStock(Base):
    """礼品库存表"""
    __tablename__ = "gift_stock"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    gift_id = Column(Integer, ForeignKey("gift.id"), unique=True, nullable=False, comment="礼品ID")
    current_stock = Column(Integer, default=0, comment="当前库存（不可为负）")
    total_in_stock = Column(Integer, default=0, comment="累计入库量")
    total_out_stock = Column(Integer, default=0, comment="累计出库量")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="库存更新时间")
    
    # 关系
    gift = relationship("Gift", back_populates="stock")
