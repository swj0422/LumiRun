from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class SysLog(Base):
    """系统操作日志表"""
    __tablename__ = "sys_log"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("sys_user.id"), nullable=False, comment="操作人ID")
    action = Column(String(50), nullable=False, comment="操作类型")
    target = Column(String(50), nullable=False, comment="操作目标")
    target_id = Column(Integer, comment="操作目标ID")
    detail = Column(Text, comment="操作详情")
    ip_address = Column(String(50), comment="操作IP地址")
    created_at = Column(DateTime, default=datetime.utcnow, comment="操作时间")
    
    # 关系
    user = relationship("User", back_populates="sys_logs")
