from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class InputType(str, enum.Enum):
    MANUAL = "1"  # 手动录入
    VOICE = "2"  # 语音录入
    BATCH = "3"  # 批量导入
    SYSTEM = "4"  # 系统调整


class Growth(Base):
    """成长值流水表"""
    __tablename__ = "growth"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # user_id 字段保留但标记为废弃，因为有外键约束无法直接删除
    user_id = Column(Integer, ForeignKey("sys_user.id"), nullable=True, comment="学员ID（废弃，使用class_student_id）")
    class_student_id = Column(Integer, ForeignKey("class_student.id"), nullable=False, index=True, comment="班级学员ID（唯一标识）")
    class_id = Column(Integer, ForeignKey("class_info.id"), nullable=False, index=True, comment="班级ID")
    teacher_id = Column(Integer, ForeignKey("sys_user.id"), nullable=False, comment="导师ID")
    change_value = Column(Integer, nullable=False, comment="成长值变动值（正数：加分，负数：减分）")
    reason = Column(Text, nullable=False, comment="变动原因")
    operator_id = Column(Integer, ForeignKey("sys_user.id"), nullable=False, comment="操作导师ID")
    input_type = Column(Integer, default=1, comment="录入方式：1-手动录入，2-语音录入，3-批量导入，4-系统调整")
    class_status = Column(Boolean, comment="操作时的班级状态")
    created_at = Column(DateTime, default=datetime.utcnow, comment="变动时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="最后修改时间")
    
    # 关系
    # 移除与 User 模型的直接关系，使用 class_student 间接关联
    # user = relationship("User", back_populates="growth_logs", foreign_keys=[user_id])
    class_student = relationship("ClassStudent", back_populates="growth_logs")
    class_info = relationship("ClassInfo", back_populates="growth_logs")
    teacher = relationship("User", foreign_keys=[teacher_id])
    operator = relationship("User", foreign_keys=[operator_id])
    # 通过 class_student 间接关联到 student_profile
    @property
    def student_profile(self):
        if self.class_student:
            return self.class_student.student_profile
        return None
