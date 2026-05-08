from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Boolean, Text, String
from sqlalchemy.orm import relationship
from app.core.database import Base


class Message(Base):
    """消息通知表"""
    __tablename__ = "message"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("sys_user.id"), nullable=False, comment="用户ID")
    title = Column(String(100), nullable=False, comment="消息标题")
    content = Column(Text, nullable=False, comment="消息内容")
    is_read = Column(Boolean, default=False, comment="是否已读")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    
    # 关系
    user = relationship("User", back_populates="messages")
