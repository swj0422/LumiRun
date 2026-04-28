from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class BindStatus(str, enum.Enum):
    NONE = "none"  # 未绑定（教师直接导入）
    PENDING = "pending"  # 待审核（学员申请绑定）
    APPROVED = "approved"  # 已绑定
    REJECTED = "rejected"  # 已拒绝
    UNBOUND = "unbound"  # 已解绑（用于绑错后解除，可重新绑定）

    @classmethod
    def _missing_(cls, value):
        for member in cls:
            if member.value == value:
                return member
        return super()._missing__(value)


class ClassStudent(Base):
    """班级学员表（导师添加的学员信息和二维码绑定的学员信息）"""
    __tablename__ = "class_student"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    class_id = Column(Integer, ForeignKey("class_info.id"), nullable=False, index=True, comment="班级ID")
    student_profile_id = Column(Integer, ForeignKey("student_profile.id"), nullable=True, comment="关联的学员档案ID（学员注册后绑定）")
    name_in_class = Column(String(50), nullable=False, comment="该班内姓名（老师导入的名字）")
    student_no_in_class = Column(String(50), nullable=False, comment="该班内学号（老师导入的学号）")
    bind_status = Column(Enum(BindStatus, values_callable=lambda x: [e.value for e in x]), default=BindStatus.NONE, nullable=False, comment="绑定状态：未绑定/待审核/已绑定/已拒绝/已解绑")
    is_current = Column(Boolean, default=True, nullable=False, comment="当前班级标识：True-当前班级，False-历史班级")
    is_deleted = Column(Boolean, default=False, nullable=False, comment="是否已删除：True-已删除，False-未删除")
    is_active = Column(Boolean, default=True, nullable=False, comment="是否启用：True-启用，False-停用")
    bind_time = Column(DateTime, comment="绑定时间")
    audit_time = Column(DateTime, comment="审核时间")
    deleted_at = Column(DateTime, comment="删除时间")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    class_info = relationship("ClassInfo", back_populates="student_bindings")
    student_profile = relationship("StudentProfile", back_populates="class_students")
    growth_logs = relationship("Growth", back_populates="class_student")
    gift_orders = relationship("GiftOrder", back_populates="class_student")
    note = relationship("StudentNote", back_populates="class_student", uselist=False)
