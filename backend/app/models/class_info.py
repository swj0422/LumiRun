from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class ClassInfo(Base):
    """班级表"""
    __tablename__ = "class_info"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    school_name = Column(String(100), nullable=False, comment="学校名称")
    session = Column(String(50), nullable=False, comment="级")
    class_name = Column(String(50), nullable=False, comment="班级名称")
    description = Column(String(500), nullable=True, comment="班级描述")
    teacher_id = Column(Integer, ForeignKey("sys_user.id"), nullable=False, comment="创建导师ID")
    status = Column(Boolean, default=True, comment="班级状态：0-关闭，1-开放")
    qr_code = Column(String(64), unique=True, nullable=False, comment="班级绑定二维码唯一标识")
    qr_url = Column(String(255), comment="班级绑定二维码图片地址")
    created_at = Column(DateTime, default=datetime.now, comment="班级创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="班级更新时间")
    
    # 关系
    teacher = relationship("User", back_populates="classes")
    student_bindings = relationship("ClassStudent", back_populates="class_info")
    growth_logs = relationship("Growth", back_populates="class_info")
    gift_orders = relationship("GiftOrder", back_populates="class_info")
    verify_records = relationship("VerifyRecord", back_populates="class_info")
