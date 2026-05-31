from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.core.database import get_db
from app.core.security import get_current_user, require_teacher
from app.schemas.suggestion import (
    SuggestionPostCreate, SuggestionPostUpdate, SuggestionPostResponse,
    SuggestionCommentCreate, SuggestionCommentUpdate, SuggestionCommentResponse,
    SuggestionPostListResponse, SuggestionCommentListResponse
)
from app.services.suggestion_service import SuggestionService
from app.models.user import User
from app.core.logger import logger

router = APIRouter()


@router.post("/posts", response_model=SuggestionPostResponse)
async def create_post(
    post_data: SuggestionPostCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建意见帖子"""
    try:
        # 获取用户角色
        user_role = current_user.role.role_name if current_user.role else "学员"
        
        # 创建帖子
        post = await SuggestionService.create_post(
            db,
            post_data.title,
            post_data.content,
            current_user.id,
            current_user.real_name or current_user.username,
            user_role
        )
        
        # 构造响应
        response = SuggestionPostResponse(
            id=post.id,
            title=post.title,
            content=post.content,
            user_id=post.user_id,
            user_name=post.user_name,
            user_role=post.user_role,
            like_count=post.like_count,
            comment_count=post.comment_count,
            view_count=post.view_count,
            created_at=post.created_at,
            updated_at=post.updated_at,
            is_liked=False
        )
        
        return response
    except Exception as e:
        logger.error(f"创建意见帖子失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建帖子失败，请稍后重试"
        )


@router.get("/posts", response_model=SuggestionPostListResponse)
async def get_posts(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回的记录数"),
    order_by: str = Query("created_at", description="排序字段: created_at, like_count, comment_count"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取意见帖子列表"""
    try:
        posts, total = await SuggestionService.get_posts(
            db,
            skip=skip,
            limit=limit,
            order_by=order_by,
            current_user_id=current_user.id
        )
        
        # 构造响应
        items = []
        for post in posts:
            item = SuggestionPostResponse(
                id=post.id,
                title=post.title,
                content=post.content,
                user_id=post.user_id,
                user_name=post.user_name,
                user_role=post.user_role,
                like_count=post.like_count,
                comment_count=post.comment_count,
                view_count=post.view_count,
                created_at=post.created_at,
                updated_at=post.updated_at,
                is_liked=getattr(post, 'is_liked', False)
            )
            items.append(item)
        
        return SuggestionPostListResponse(items=items, total=total)
    except Exception as e:
        logger.error(f"获取意见帖子列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取帖子列表失败，请稍后重试"
        )


@router.get("/posts/{post_id}", response_model=SuggestionPostResponse)
async def get_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取意见帖子详情"""
    try:
        post = await SuggestionService.get_post_by_id(
            db,
            post_id=post_id,
            current_user_id=current_user.id
        )
        
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="帖子不存在或已删除"
            )
        
        # 构造响应
        response = SuggestionPostResponse(
            id=post.id,
            title=post.title,
            content=post.content,
            user_id=post.user_id,
            user_name=post.user_name,
            user_role=post.user_role,
            like_count=post.like_count,
            comment_count=post.comment_count,
            view_count=post.view_count,
            created_at=post.created_at,
            updated_at=post.updated_at,
            is_liked=getattr(post, 'is_liked', False)
        )
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取意见帖子详情失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取帖子详情失败，请稍后重试"
        )


@router.put("/posts/{post_id}", response_model=SuggestionPostResponse)
async def update_post(
    post_id: int,
    post_data: SuggestionPostUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新意见帖子"""
    try:
        post = await SuggestionService.update_post(
            db,
            post_id=post_id,
            title=post_data.title,
            content=post_data.content,
            user_id=current_user.id
        )
        
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="帖子不存在或已删除，或无权限修改"
            )
        
        # 构造响应
        response = SuggestionPostResponse(
            id=post.id,
            title=post.title,
            content=post.content,
            user_id=post.user_id,
            user_name=post.user_name,
            user_role=post.user_role,
            like_count=post.like_count,
            comment_count=post.comment_count,
            view_count=post.view_count,
            created_at=post.created_at,
            updated_at=post.updated_at,
            is_liked=False
        )
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新意见帖子失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新帖子失败，请稍后重试"
        )


@router.delete("/posts/{post_id}", response_model=dict)
async def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除意见帖子"""
    try:
        # 检查用户是否是管理员
        is_admin = current_user.role.role_name in ["super_admin", "admin"]
        
        success = await SuggestionService.delete_post(
            db,
            post_id=post_id,
            user_id=current_user.id,
            is_admin=is_admin
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="帖子不存在或已删除，或无权限删除"
            )
        
        return {"message": "帖子删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除意见帖子失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除帖子失败，请稍后重试"
        )


@router.post("/comments", response_model=SuggestionCommentResponse)
async def create_comment(
    comment_data: SuggestionCommentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建评论"""
    try:
        # 获取用户角色
        user_role = current_user.role.role_name if current_user.role else "学员"
        
        # 创建评论
        comment = await SuggestionService.create_comment(
            db,
            post_id=comment_data.post_id,
            content=comment_data.content,
            user_id=current_user.id,
            user_name=current_user.real_name or current_user.username,
            user_role=user_role
        )
        
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="帖子不存在或已删除"
            )
        
        # 构造响应
        response = SuggestionCommentResponse(
            id=comment.id,
            post_id=comment.post_id,
            content=comment.content,
            user_id=comment.user_id,
            user_name=comment.user_name,
            user_role=comment.user_role,
            created_at=comment.created_at,
            updated_at=comment.updated_at
        )
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建评论失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建评论失败，请稍后重试"
        )


@router.get("/posts/{post_id}/comments", response_model=SuggestionCommentListResponse)
async def get_comments(
    post_id: int,
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回的记录数"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取帖子的评论列表"""
    try:
        comments, total = await SuggestionService.get_comments(
            db,
            post_id=post_id,
            skip=skip,
            limit=limit
        )
        
        # 构造响应
        items = []
        for comment in comments:
            item = SuggestionCommentResponse(
                id=comment.id,
                post_id=comment.post_id,
                content=comment.content,
                user_id=comment.user_id,
                user_name=comment.user_name,
                user_role=comment.user_role,
                created_at=comment.created_at,
                updated_at=comment.updated_at
            )
            items.append(item)
        
        return SuggestionCommentListResponse(items=items, total=total)
    except Exception as e:
        logger.error(f"获取评论列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取评论列表失败，请稍后重试"
        )


@router.put("/comments/{comment_id}", response_model=SuggestionCommentResponse)
async def update_comment(
    comment_id: int,
    comment_data: SuggestionCommentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新评论"""
    try:
        comment = await SuggestionService.update_comment(
            db,
            comment_id=comment_id,
            content=comment_data.content,
            user_id=current_user.id
        )
        
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="评论不存在或已删除，或无权限修改"
            )
        
        # 构造响应
        response = SuggestionCommentResponse(
            id=comment.id,
            post_id=comment.post_id,
            content=comment.content,
            user_id=comment.user_id,
            user_name=comment.user_name,
            user_role=comment.user_role,
            created_at=comment.created_at,
            updated_at=comment.updated_at
        )
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新评论失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新评论失败，请稍后重试"
        )


@router.delete("/comments/{comment_id}", response_model=dict)
async def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除评论"""
    try:
        # 检查用户是否是管理员
        is_admin = current_user.role.role_name in ["super_admin", "admin"]
        
        success = await SuggestionService.delete_comment(
            db,
            comment_id=comment_id,
            user_id=current_user.id,
            is_admin=is_admin
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="评论不存在或已删除，或无权限删除"
            )
        
        return {"message": "评论删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除评论失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除评论失败，请稍后重试"
        )


@router.post("/posts/{post_id}/like", response_model=dict)
async def toggle_like(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """点赞/取消点赞"""
    try:
        result = await SuggestionService.toggle_like(
            db,
            post_id=post_id,
            user_id=current_user.id
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["message"]
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"点赞/取消点赞失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="操作失败，请稍后重试"
        )


@router.get("/user/posts", response_model=SuggestionPostListResponse)
async def get_user_posts(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回的记录数"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取用户发布的帖子"""
    try:
        posts, total = await SuggestionService.get_user_posts(
            db,
            user_id=current_user.id,
            skip=skip,
            limit=limit
        )
        
        # 构造响应
        items = []
        for post in posts:
            item = SuggestionPostResponse(
                id=post.id,
                title=post.title,
                content=post.content,
                user_id=post.user_id,
                user_name=post.user_name,
                user_role=post.user_role,
                like_count=post.like_count,
                comment_count=post.comment_count,
                view_count=post.view_count,
                created_at=post.created_at,
                updated_at=post.updated_at,
                is_liked=getattr(post, 'is_liked', False)
            )
            items.append(item)
        
        return SuggestionPostListResponse(items=items, total=total)
    except Exception as e:
        logger.error(f"获取用户帖子列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户帖子列表失败，请稍后重试"
        )
