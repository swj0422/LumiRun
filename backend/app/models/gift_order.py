from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class GiftOrder(Base):
    """兑换订单表"""
    __tablename__ = "gift_order"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    class_student_id = Column(Integer, ForeignKey("class_student.id"), nullable=False, comment="学员ID")
    gift_id = Column(Integer, ForeignKey("gift.id"), nullable=False, comment="礼品ID")
    class_id = Column(Integer, ForeignKey("class_info.id"), nullable=False, comment="班级ID")
    teacher_id = Column(Integer, ForeignKey("sys_user.id"), nullable=False, comment="导师ID")
    creator_id = Column(Integer, ForeignKey("sys_user.id"), nullable=True, comment="创建人ID（发起兑换的用户ID）")
    operator_id = Column(Integer, ForeignKey("sys_user.id"), nullable=True, comment="当前操作人ID")
    price = Column(Integer, nullable=False, comment="兑换消耗的成长值")
    status = Column(Integer, default=0, index=True, comment="订单状态：0-待审核，1-待核销，2-已完成，3-已取消")
    qr_code = Column(String(64), unique=True, nullable=False, comment="订单核销二维码唯一标识")
    cancel_reason = Column(String(255), comment="取消原因")
    created_at = Column(DateTime, default=datetime.utcnow, comment="订单创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="订单状态更新时间")
    
    # 关系
    class_student = relationship("ClassStudent", back_populates="gift_orders")
    gift = relationship("Gift", back_populates="orders")
    class_info = relationship("ClassInfo", back_populates="gift_orders")
    teacher = relationship("User", back_populates="teacher_orders", foreign_keys=[teacher_id])
    creator = relationship("User", foreign_keys=[creator_id])
    operator = relationship("User", foreign_keys=[operator_id])
    verify_record = relationship("VerifyRecord", back_populates="order", uselist=False)
