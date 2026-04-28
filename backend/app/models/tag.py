from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class TagType(str, enum.Enum):
    """标签类型枚举"""
    STUDENT = "student"
    GROWTH = "growth"
    GIFT = "gift"


class Tag(Base):
    """标签表"""
    __tablename__ = "tag"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), nullable=False, comment="标签名称")
    type = Column(SQLEnum(TagType), nullable=False, comment="标签类型")
    description = Column(Text, nullable=True, comment="标签描述")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
