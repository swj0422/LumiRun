from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base


class Role(Base):
    """角色表"""
    __tablename__ = "sys_role"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    role_name = Column(String(50), unique=True, nullable=False, comment="角色名称")
    remark = Column(String(255), comment="角色说明")
    
    # 关系
    users = relationship("User", back_populates="role")
    permissions = relationship("Permission", secondary="sys_role_permission", back_populates="roles")


class User(Base):
    """用户表"""
    __tablename__ = "sys_user"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(100), unique=True, nullable=False, comment="邮箱（用于找回密码）")
    username = Column(String(50), unique=True, nullable=False, comment="用户名（登录账号）")
    password = Column(String(255), nullable=False, comment="密码（加密存储）")
    real_name = Column(String(50), nullable=False, comment="真实姓名")
    phone = Column(String(20), nullable=True, comment="手机号（选填）")
    role_id = Column(Integer, ForeignKey("sys_role.id"), nullable=False, comment="角色ID")
    status = Column(Boolean, default=True, comment="账号状态：0-禁用，1-启用")
    last_login_time = Column(DateTime, comment="最后登录时间")
    login_count = Column(Integer, default=0, comment="登录次数")
    login_error_count = Column(Integer, default=0, comment="连续登录错误次数")
    locked_until = Column(DateTime, nullable=True, comment="账号锁定截止时间")
    password_reset_token = Column(String(100), nullable=True, comment="密码重置令牌")
    password_reset_expires = Column(DateTime, nullable=True, comment="密码重置令牌过期时间")
    created_at = Column(DateTime, default=datetime.now, comment="账号创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="账号更新时间")
    
    # 关系
    role = relationship("Role", back_populates="users")
    classes = relationship("ClassInfo", back_populates="teacher", foreign_keys="ClassInfo.teacher_id")
    # 移除与 GrowthScore 的关系，不再使用该表
    # growth_scores = relationship("GrowthScore", back_populates="user", uselist=False)
    # 移除与 GrowthLog 的直接关系，使用 class_student 间接关联
    # growth_logs = relationship("GrowthLog", back_populates="user", foreign_keys="GrowthLog.user_id")
    student_profile = relationship("StudentProfile", back_populates="user", uselist=False)
    gifts = relationship("Gift", back_populates="teacher")
    teacher_orders = relationship("GiftOrder", back_populates="teacher", foreign_keys="GiftOrder.teacher_id")
    user_wishes = relationship("Wish", back_populates="user")
    messages = relationship("Message", back_populates="user")
    system_logs = relationship("SystemLog", back_populates="user")
    sys_logs = relationship("SysLog", back_populates="user")
    # 移除与 GrowthReason 的关系，不再使用该表
    # growth_reasons = relationship("GrowthReason", back_populates="teacher")
