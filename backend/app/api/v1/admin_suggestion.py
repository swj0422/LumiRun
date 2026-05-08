from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from app.core.database import get_db
from app.core.security import require_admin
from app.models.user import User
from app.models.suggestion import SuggestionPost, SuggestionComment, SuggestionLike

router = APIRouter()


@router.get("/suggestions")
async def get_admin_suggestions(
    user_id: Optional[int] = Query(None, description="用户ID"),
    user_role: Optional[str] = Query(None, description="用户角色"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    query = select(SuggestionPost)
    
    if user_id:
        query = query.where(SuggestionPost.user_id == user_id)
    if user_role:
        query = query.where(SuggestionPost.user_role == user_role)
    if keyword:
        query = query.where(SuggestionPost.title.contains(keyword) | SuggestionPost.content.contains(keyword))
    query = query.where(SuggestionPost.is_deleted == 0)
    
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0
    
    query = query.order_by(SuggestionPost.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    suggestions = result.scalars().all()
    
    suggestion_list = []
    for suggestion in suggestions:
        suggestion_list.append({
            "id": suggestion.id,
            "title": suggestion.title,
            "content": suggestion.content,
            "user_id": suggestion.user_id,
            "user_name": suggestion.user_name,
            "user_role": suggestion.user_role,
            "like_count": suggestion.like_count,
            "comment_count": suggestion.comment_count,
            "view_count": suggestion.view_count,
            "created_at": suggestion.created_at,
            "updated_at": suggestion.updated_at
        })
    
    return {
        "items": suggestion_list,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/suggestions/{suggestion_id}")
async def get_suggestion_detail(
    suggestion_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    suggestion = await db.get(SuggestionPost, suggestion_id)
    
    if not suggestion or suggestion.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="建议不存在"
        )
    
    comments_query = select(SuggestionComment).where(
        SuggestionComment.post_id == suggestion_id,
        SuggestionComment.is_deleted == 0
    ).order_by(SuggestionComment.created_at.desc())
    comments_result = await db.execute(comments_query)
    comments = comments_result.scalars().all()
    
    comment_list = []
    for comment in comments:
        comment_list.append({
            "id": comment.id,
            "content": comment.content,
            "user_id": comment.user_id,
            "user_name": comment.user_name,
            "user_role": comment.user_role,
            "created_at": comment.created_at
        })
    
    return {
        "id": suggestion.id,
        "title": suggestion.title,
        "content": suggestion.content,
        "user_id": suggestion.user_id,
        "user_name": suggestion.user_name,
        "user_role": suggestion.user_role,
        "like_count": suggestion.like_count,
        "comment_count": suggestion.comment_count,
        "view_count": suggestion.view_count,
        "created_at": suggestion.created_at,
        "updated_at": suggestion.updated_at,
        "comments": comment_list
    }


@router.delete("/suggestions/{suggestion_id}")
async def delete_suggestion(
    suggestion_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    from app.models.system_log import SystemLog, LogType, LogLevel
    
    suggestion = await db.get(SuggestionPost, suggestion_id)
    if not suggestion or suggestion.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="建议不存在"
        )
    
    suggestion.is_deleted = 1
    
    system_log = SystemLog(
        user_id=current_user.id,
        username=current_user.username,
        real_name=current_user.real_name,
        log_type=LogType.DELETE,
        log_level=LogLevel.INFO,
        module="建议管理",
        action="删除建议",
        biz_type="suggestion",
        biz_id=suggestion_id,
        request_params=f'{{"suggestion_id": {suggestion_id}}}',
        before_data=f'{{"标题": "{suggestion.title}", "用户": "{suggestion.user_name}"}}'
    )
    db.add(system_log)
    
    await db.commit()
    
    return {"message": "删除成功"}
