from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from app.core.database import Base


class SuggestionPost(Base):
    """意见主表"""
    __tablename__ = "suggestion_post"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, comment="标题")
    content = Column(Text, nullable=False, comment="内容")
    user_id = Column(Integer, nullable=False, comment="发布人ID")
    user_name = Column(String(50), nullable=False, comment="发布人姓名（快照）")
    user_role = Column(String(20), nullable=False, comment="发布人角色")
    like_count = Column(Integer, default=0, comment="点赞数")
    comment_count = Column(Integer, default=0, comment="评论数")
    view_count = Column(Integer, default=0, comment="浏览数")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    is_deleted = Column(Integer, default=0, comment="伪删除，0-正常，1-已删除")


class SuggestionComment(Base):
    """评论表"""
    __tablename__ = "suggestion_comment"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("suggestion_post.id"), nullable=False, comment="关联帖子ID")
    content = Column(Text, nullable=False, comment="评论内容")
    user_id = Column(Integer, nullable=False, comment="评论人ID")
    user_name = Column(String(50), nullable=False, comment="评论人姓名（快照）")
    user_role = Column(String(20), nullable=False, comment="评论人角色")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    is_deleted = Column(Integer, default=0, comment="伪删除，0-正常，1-已删除")


class SuggestionLike(Base):
    """点赞表"""
    __tablename__ = "suggestion_like"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("suggestion_post.id"), nullable=False, comment="帖子ID")
    user_id = Column(Integer, nullable=False, comment="点赞人ID")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    
    # 唯一约束，防止重复点赞
    __table_args__ = (
        UniqueConstraint('post_id', 'user_id', name='_post_user_uc'),
    )
