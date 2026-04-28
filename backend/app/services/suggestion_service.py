from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from app.models.suggestion import SuggestionPost, SuggestionComment, SuggestionLike
from app.core.logger import logger


class SuggestionService:
    """意见征集服务类"""
    
    @staticmethod
    async def create_post(
        db: AsyncSession,
        title: str,
        content: str,
        user_id: int,
        user_name: str,
        user_role: str
    ) -> SuggestionPost:
        """创建意见帖子"""
        try:
            post = SuggestionPost(
                title=title,
                content=content,
                user_id=user_id,
                user_name=user_name,
                user_role=user_role
            )
            db.add(post)
            await db.commit()
            await db.refresh(post)
            logger.info(f"创建意见帖子成功: user_id={user_id}, title={title}")
            return post
        except Exception as e:
            await db.rollback()
            logger.error(f"创建意见帖子失败: {e}")
            raise
    
    @staticmethod
    async def get_posts(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        order_by: str = "created_at",
        current_user_id: Optional[int] = None
    ) -> tuple[List[SuggestionPost], int]:
        """获取意见帖子列表"""
        try:
            # 构建查询
            query = select(SuggestionPost).where(SuggestionPost.is_deleted == 0)
            
            # 排序
            if order_by == "like_count":
                query = query.order_by(desc(SuggestionPost.like_count), desc(SuggestionPost.created_at))
            elif order_by == "comment_count":
                query = query.order_by(desc(SuggestionPost.comment_count), desc(SuggestionPost.created_at))
            else:
                query = query.order_by(desc(SuggestionPost.created_at))
            
            # 计算总数
            count_query = select(func.count(SuggestionPost.id)).where(SuggestionPost.is_deleted == 0)
            count_result = await db.execute(count_query)
            total = count_result.scalar() or 0
            
            # 分页
            query = query.offset(skip).limit(limit)
            
            # 执行查询
            result = await db.execute(query)
            posts = result.scalars().all()
            
            # 如果提供了当前用户ID，查询用户是否点赞
            if current_user_id:
                for post in posts:
                    like_query = select(SuggestionLike).where(
                        and_(
                            SuggestionLike.post_id == post.id,
                            SuggestionLike.user_id == current_user_id
                        )
                    )
                    like_result = await db.execute(like_query)
                    post.is_liked = like_result.scalar() is not None
            
            logger.info(f"获取意见帖子列表成功: total={total}, skip={skip}, limit={limit}")
            return posts, total
        except Exception as e:
            logger.error(f"获取意见帖子列表失败: {e}")
            return [], 0
    
    @staticmethod
    async def get_post_by_id(
        db: AsyncSession,
        post_id: int,
        current_user_id: Optional[int] = None
    ) -> Optional[SuggestionPost]:
        """根据ID获取意见帖子"""
        try:
            query = select(SuggestionPost).where(
                and_(
                    SuggestionPost.id == post_id,
                    SuggestionPost.is_deleted == 0
                )
            )
            result = await db.execute(query)
            post = result.scalar_one_or_none()
            
            if post:
                # 增加浏览数
                post.view_count += 1
                await db.commit()
                await db.refresh(post)
                
                # 如果提供了当前用户ID，查询用户是否点赞
                if current_user_id:
                    like_query = select(SuggestionLike).where(
                        and_(
                            SuggestionLike.post_id == post.id,
                            SuggestionLike.user_id == current_user_id
                        )
                    )
                    like_result = await db.execute(like_query)
                    post.is_liked = like_result.scalar() is not None
            
            logger.info(f"获取意见帖子详情成功: post_id={post_id}")
            return post
        except Exception as e:
            logger.error(f"获取意见帖子详情失败: {e}")
            return None
    
    @staticmethod
    async def update_post(
        db: AsyncSession,
        post_id: int,
        user_id: int,
        title: Optional[str] = None,
        content: Optional[str] = None
    ) -> Optional[SuggestionPost]:
        """更新意见帖子"""
        try:
            # 首先检查帖子是否存在且未删除
            post = await db.get(SuggestionPost, post_id)
            if not post or post.is_deleted == 1:
                return None
            
            # 检查是否是帖子作者
            if post.user_id != user_id:
                return None
            
            # 更新帖子
            if title:
                post.title = title
            if content:
                post.content = content
            
            await db.commit()
            await db.refresh(post)
            logger.info(f"更新意见帖子成功: post_id={post_id}, user_id={user_id}")
            return post
        except Exception as e:
            await db.rollback()
            logger.error(f"更新意见帖子失败: {e}")
            return None
    
    @staticmethod
    async def delete_post(
        db: AsyncSession,
        post_id: int,
        user_id: int,
        is_admin: bool = False
    ) -> bool:
        """删除意见帖子"""
        try:
            # 首先检查帖子是否存在且未删除
            post = await db.get(SuggestionPost, post_id)
            if not post or post.is_deleted == 1:
                return False
            
            # 检查是否是帖子作者或管理员
            if post.user_id != user_id and not is_admin:
                return False
            
            # 伪删除帖子
            post.is_deleted = 1
            await db.commit()
            logger.info(f"删除意见帖子成功: post_id={post_id}, user_id={user_id}, is_admin={is_admin}")
            return True
        except Exception as e:
            await db.rollback()
            logger.error(f"删除意见帖子失败: {e}")
            return False
    
    @staticmethod
    async def create_comment(
        db: AsyncSession,
        post_id: int,
        content: str,
        user_id: int,
        user_name: str,
        user_role: str
    ) -> Optional[SuggestionComment]:
        """创建评论"""
        try:
            # 首先检查帖子是否存在且未删除
            post = await db.get(SuggestionPost, post_id)
            if not post or post.is_deleted == 1:
                return None
            
            # 创建评论
            comment = SuggestionComment(
                post_id=post_id,
                content=content,
                user_id=user_id,
                user_name=user_name,
                user_role=user_role
            )
            db.add(comment)
            
            # 更新帖子的评论数
            post.comment_count += 1
            
            await db.commit()
            await db.refresh(comment)
            logger.info(f"创建评论成功: post_id={post_id}, user_id={user_id}")
            return comment
        except Exception as e:
            await db.rollback()
            logger.error(f"创建评论失败: {e}")
            return None
    
    @staticmethod
    async def get_comments(
        db: AsyncSession,
        post_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[SuggestionComment], int]:
        """获取帖子的评论列表"""
        try:
            # 构建查询
            query = select(SuggestionComment).where(
                and_(
                    SuggestionComment.post_id == post_id,
                    SuggestionComment.is_deleted == 0
                )
            ).order_by(desc(SuggestionComment.created_at))
            
            # 计算总数
            count_query = select(func.count(SuggestionComment.id)).where(
                and_(
                    SuggestionComment.post_id == post_id,
                    SuggestionComment.is_deleted == 0
                )
            )
            count_result = await db.execute(count_query)
            total = count_result.scalar() or 0
            
            # 分页
            query = query.offset(skip).limit(limit)
            
            # 执行查询
            result = await db.execute(query)
            comments = result.scalars().all()
            
            logger.info(f"获取评论列表成功: post_id={post_id}, total={total}, skip={skip}, limit={limit}")
            return comments, total
        except Exception as e:
            logger.error(f"获取评论列表失败: {e}")
            return [], 0
    
    @staticmethod
    async def update_comment(
        db: AsyncSession,
        comment_id: int,
        content: str,
        user_id: int
    ) -> Optional[SuggestionComment]:
        """更新评论"""
        try:
            # 首先检查评论是否存在且未删除
            comment = await db.get(SuggestionComment, comment_id)
            if not comment or comment.is_deleted == 1:
                return None
            
            # 检查是否是评论作者
            if comment.user_id != user_id:
                return None
            
            # 更新评论
            comment.content = content
            await db.commit()
            await db.refresh(comment)
            logger.info(f"更新评论成功: comment_id={comment_id}, user_id={user_id}")
            return comment
        except Exception as e:
            await db.rollback()
            logger.error(f"更新评论失败: {e}")
            return None
    
    @staticmethod
    async def delete_comment(
        db: AsyncSession,
        comment_id: int,
        user_id: int,
        is_admin: bool = False
    ) -> bool:
        """删除评论"""
        try:
            # 首先检查评论是否存在且未删除
            comment = await db.get(SuggestionComment, comment_id)
            if not comment or comment.is_deleted == 1:
                return False
            
            # 检查是否是评论作者或管理员
            if comment.user_id != user_id and not is_admin:
                return False
            
            # 伪删除评论
            comment.is_deleted = 1
            
            # 更新帖子的评论数
            post = await db.get(SuggestionPost, comment.post_id)
            if post and post.comment_count > 0:
                post.comment_count -= 1
            
            await db.commit()
            logger.info(f"删除评论成功: comment_id={comment_id}, user_id={user_id}, is_admin={is_admin}")
            return True
        except Exception as e:
            await db.rollback()
            logger.error(f"删除评论失败: {e}")
            return False
    
    @staticmethod
    async def toggle_like(
        db: AsyncSession,
        post_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """点赞/取消点赞"""
        try:
            # 首先检查帖子是否存在且未删除
            post = await db.get(SuggestionPost, post_id)
            if not post or post.is_deleted == 1:
                return {"success": False, "message": "帖子不存在或已删除"}
            
            # 检查用户是否已经点赞
            like_query = select(SuggestionLike).where(
                and_(
                    SuggestionLike.post_id == post_id,
                    SuggestionLike.user_id == user_id
                )
            )
            like_result = await db.execute(like_query)
            existing_like = like_result.scalar_one_or_none()
            
            if existing_like:
                # 取消点赞
                await db.delete(existing_like)
                post.like_count = max(0, post.like_count - 1)
                action = "unlike"
            else:
                # 点赞
                new_like = SuggestionLike(post_id=post_id, user_id=user_id)
                db.add(new_like)
                post.like_count += 1
                action = "like"
            
            await db.commit()
            await db.refresh(post)
            logger.info(f"{action} 成功: post_id={post_id}, user_id={user_id}")
            return {
                "success": True,
                "action": action,
                "like_count": post.like_count,
                "is_liked": action == "like"
            }
        except Exception as e:
            await db.rollback()
            logger.error(f"点赞/取消点赞失败: {e}")
            return {"success": False, "message": "操作失败，请稍后重试"}
    
    @staticmethod
    async def get_user_posts(
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[SuggestionPost], int]:
        """获取用户发布的帖子"""
        try:
            # 构建查询
            query = select(SuggestionPost).where(
                and_(
                    SuggestionPost.user_id == user_id,
                    SuggestionPost.is_deleted == 0
                )
            ).order_by(desc(SuggestionPost.created_at))
            
            # 计算总数
            count_query = select(func.count(SuggestionPost.id)).where(
                and_(
                    SuggestionPost.user_id == user_id,
                    SuggestionPost.is_deleted == 0
                )
            )
            count_result = await db.execute(count_query)
            total = count_result.scalar() or 0
            
            # 分页
            query = query.offset(skip).limit(limit)
            
            # 执行查询
            result = await db.execute(query)
            posts = result.scalars().all()
            
            # 查询用户是否点赞
            for post in posts:
                like_query = select(SuggestionLike).where(
                    and_(
                        SuggestionLike.post_id == post.id,
                        SuggestionLike.user_id == user_id
                    )
                )
                like_result = await db.execute(like_query)
                post.is_liked = like_result.scalar() is not None
            
            logger.info(f"获取用户帖子列表成功: user_id={user_id}, total={total}, skip={skip}, limit={limit}")
            return posts, total
        except Exception as e:
            logger.error(f"获取用户帖子列表失败: {e}")
            return [], 0
