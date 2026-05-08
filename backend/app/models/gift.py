from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class Gift(Base):
    """礼品基础信息表"""
    __tablename__ = "gift"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, comment="礼品名称")
    description = Column(Text, comment="礼品描述")
    image_url = Column(String(255), comment="奖励图片地址")
    price = Column(Integer, nullable=False, comment="兑换所需成长值")
    status = Column(Boolean, default=True, comment="礼品状态：0-下架，1-上架")
    warning_stock = Column(Integer, default=10, comment="库存预警阈值")
    teacher_id = Column(Integer, ForeignKey("sys_user.id"), nullable=False, comment="创建导师ID")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关系
    teacher = relationship("User", back_populates="gifts")
    orders = relationship("GiftOrder", back_populates="gift")
    stock = relationship("GiftStock", back_populates="gift", uselist=False)
    class_relations = relationship("GiftClassRelation", back_populates="gift")
