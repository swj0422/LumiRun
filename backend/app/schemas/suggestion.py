from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SuggestionPostBase(BaseModel):
    """意见帖子基础模型"""
    title: str = Field(..., max_length=200, description="标题")
    content: str = Field(..., description="内容")


class SuggestionPostCreate(SuggestionPostBase):
    """创建意见帖子模型"""
    pass


class SuggestionPostUpdate(BaseModel):
    """更新意见帖子模型"""
    title: Optional[str] = Field(None, max_length=200, description="标题")
    content: Optional[str] = Field(None, description="内容")


class SuggestionPostResponse(SuggestionPostBase):
    """意见帖子响应模型"""
    id: int
    user_id: int
    user_name: str
    user_role: str
    like_count: int
    comment_count: int
    view_count: int
    created_at: datetime
    updated_at: datetime
    is_liked: bool = False  # 当前用户是否点赞
    
    class Config:
        from_attributes = True


class SuggestionCommentBase(BaseModel):
    """评论基础模型"""
    content: str = Field(..., description="评论内容")


class SuggestionCommentCreate(SuggestionCommentBase):
    """创建评论模型"""
    post_id: int = Field(..., description="帖子ID")


class SuggestionCommentUpdate(BaseModel):
    """更新评论模型"""
    content: str = Field(..., description="评论内容")


class SuggestionCommentResponse(SuggestionCommentBase):
    """评论响应模型"""
    id: int
    post_id: int
    user_id: int
    user_name: str
    user_role: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SuggestionLikeResponse(BaseModel):
    """点赞响应模型"""
    id: int
    post_id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class SuggestionPostListResponse(BaseModel):
    """意见帖子列表响应模型"""
    items: List[SuggestionPostResponse]
    total: int


class SuggestionCommentListResponse(BaseModel):
    """评论列表响应模型"""
    items: List[SuggestionCommentResponse]
    total: int
