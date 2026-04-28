from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class Message(Base):
    """消息通知表"""
    __tablename__ = "message"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("sys_user.id"), nullable=False, comment="接收通知的学员ID")
    content = Column(Text, nullable=False, comment="通知内容")
    type = Column(Integer, nullable=False, comment="通知类型：1-解绑通知，2-礼品补货通知，3-成长值变动通知，4-订单状态通知")
    is_read = Column(Boolean, default=False, comment="是否已读：0-未读，1-已读")
    created_at = Column(DateTime, default=datetime.utcnow, comment="通知发送时间")
    
    # 关系
    user = relationship("User", back_populates="messages")
