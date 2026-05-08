from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from app.core.database import Base


class SystemSettings(Base):
    """绯荤粺璁剧疆琛?""
    __tablename__ = "sys_settings"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    setting_key = Column(String(100), unique=True, nullable=False, comment="璁剧疆閿?)
    setting_value = Column(Text, nullable=True, comment="璁剧疆鍊?)
    setting_type = Column(String(50), default="string", comment="璁剧疆绫诲瀷锛歴tring/number/boolean/json")
    category = Column(String(50), default="general", comment="璁剧疆鍒嗙被锛歡eneral/security/upload/email/feature")
    description = Column(String(255), nullable=True, comment="璁剧疆鎻忚堪")
    created_at = Column(DateTime, default=datetime.utcnow, comment="鍒涘缓鏃堕棿")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="鏇存柊鏃堕棿")
