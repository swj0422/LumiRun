from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from app.core.database import Base


class Wish(Base):
    """心愿便利贴表"""
    __tablename__ = "wish"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("sys_user.id"), nullable=False, comment="发布人ID")
    class_student_id = Column(Integer, ForeignKey("class_student.id"), nullable=True, comment="学员ID（关联绑定记录，可选）")
    content = Column(String(200), nullable=False, comment="心愿文字内容（1-200字）")
    image_url = Column(String(255), nullable=True, comment="图片地址")
    is_anonymous = Column(Integer, default=0, nullable=False, comment="是否匿名：1-匿名，0-不匿名")
    is_deleted = Column(Integer, default=0, nullable=False, comment="是否已删除：0-正常，1-已删除")
    created_at = Column(DateTime, default=datetime.now, nullable=False, comment="发布时间")
    
    # 关系
    user = relationship("User", back_populates="user_wishes")
