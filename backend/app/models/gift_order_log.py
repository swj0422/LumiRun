from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class GiftOrderLog(Base):
    """兑换订单操作记录表（历史数据）"""
    __tablename__ = "gift_order_log"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, nullable=False, index=True, comment="订单ID")
    class_student_id = Column(Integer, ForeignKey("class_student.id"), nullable=False, comment="学员ID")
    gift_id = Column(Integer, ForeignKey("gift.id"), nullable=False, comment="礼品ID")
    class_id = Column(Integer, ForeignKey("class_info.id"), nullable=False, comment="班级ID")
    teacher_id = Column(Integer, ForeignKey("sys_user.id"), nullable=False, comment="导师ID")
    creator_id = Column(Integer, ForeignKey("sys_user.id"), nullable=True, comment="创建人ID（发起兑换的用户ID）")
    operator_id = Column(Integer, ForeignKey("sys_user.id"), nullable=True, comment="操作人ID")
    price = Column(Integer, nullable=False, comment="兑换消耗的成长值")
    status = Column(Integer, default=0, comment="订单状态：0-待审核，1-待核销，2-已完成，3-已取消")
    qr_code = Column(String(64), nullable=False, comment="订单核销二维码唯一标识")
    cancel_reason = Column(String(255), comment="取消原因")
    action = Column(String(32), nullable=False, comment="操作类型：create-创建，approve-审核通过，reject-拒绝，verify-核销")
    remarks = Column(Text, comment="备注")
    created_at = Column(DateTime, default=datetime.utcnow, comment="订单创建时间")
    operated_at = Column(DateTime, default=datetime.utcnow, comment="操作时间")

    # 关系
    class_student = relationship("ClassStudent")
    gift = relationship("Gift")
    class_info = relationship("ClassInfo")
    teacher = relationship("User", foreign_keys=[teacher_id])
    creator = relationship("User", foreign_keys=[creator_id])
    operator = relationship("User", foreign_keys=[operator_id])