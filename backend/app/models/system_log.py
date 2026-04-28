from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class LogType(str, enum.Enum):
    LOGIN = "login"
    LOGOUT = "logout"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    EXCHANGE = "exchange"
    AUDIT = "audit"
    OTHER = "other"


class LogLevel(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class SystemLog(Base):
    """系统日志表"""
    __tablename__ = "system_log"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("sys_user.id"), nullable=True, comment="操作用户ID")
    username = Column(String(50), nullable=True, comment="操作用户名")
    real_name = Column(String(50), nullable=True, comment="操作用户真实姓名")
    log_type = Column(Enum(LogType, values_callable=lambda x: [e.value for e in x]), nullable=False, comment="日志类型")
    log_level = Column(Enum(LogLevel, values_callable=lambda x: [e.value for e in x]), default=LogLevel.INFO, nullable=False, comment="日志级别")
    module = Column(String(100), nullable=False, comment="操作模块")
    action = Column(String(100), nullable=False, comment="操作动作")
    biz_type = Column(String(50), nullable=True, comment="业务类型")
    biz_id = Column(Integer, nullable=True, comment="业务ID")
    ip_address = Column(String(50), nullable=True, comment="操作IP地址")
    user_agent = Column(String(500), nullable=True, comment="用户代理")
    request_url = Column(String(500), nullable=True, comment="请求URL")
    request_method = Column(String(10), nullable=True, comment="请求方法")
    request_params = Column(Text, nullable=True, comment="请求参数")
    response_status = Column(Integer, nullable=True, comment="响应状态码")
    error_message = Column(Text, nullable=True, comment="错误信息")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="日志创建时间")
    
    # 关系
    user = relationship("User", back_populates="system_logs")
