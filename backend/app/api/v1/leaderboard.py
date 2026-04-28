from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.core.database import get_db
from app.core.security import get_current_user
from app.services.growth_service import GrowthService
from app.models.user import User
from app.core.cache import cache_result

router = APIRouter()


@router.get("/class/{class_id}", response_model=List[dict])
async def get_class_leaderboard(
    class_id: int,
    order_by: str = Query("total_score", description="排序字段: total_score/available_score"),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = Query(None, description="状态: approved/pending/rejected/stopped"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取班级排行榜"""
    # 检查班级是否属于当前导师或班级助理
    from app.services.class_service import ClassService
    from app.services.class_assistant_service import ClassAssistantService
    
    class_info = await ClassService.get_class_by_id(db, class_id)
    if not class_info:
        return []
    
    # 检查是否是导师或班级助理
    is_teacher = class_info.teacher_id == current_user.id
    is_assistant = await ClassAssistantService.is_assistant_of_class(db, current_user.id, class_id)
    
    if not is_teacher and not is_assistant:
        return []
    
    # 生成缓存键
    # 添加版本号，确保代码修改后缓存会更新
    cache_key = f"leaderboard:v1:class:{current_user.id}:{class_id}:{order_by}:{limit}:{status}"
    from app.core.cache import cache
    
    # 尝试从缓存获取
    cached_result = await cache.get(cache_key)
    if cached_result:
        return cached_result
    
    leaderboard = await GrowthService.get_leaderboard(db, current_user.id, class_id, order_by, limit, status)
    
    # 处理排行榜数据
    result = []
    for rank, student in enumerate(leaderboard, 1):
        result.append({
            "rank": rank,
            "id": student["id"],
            "real_name": student["real_name"],
            "total_score": student["total_score"],
            "available_score": student["available_score"]
        })
    
    # 缓存结果，5分钟过期
    await cache.set(cache_key, result, expire=300)
    
    return result


@router.get("/all", response_model=List[dict])
async def get_all_leaderboard(
    order_by: str = Query("total_score", description="排序字段: total_score/available_score"),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = Query(None, description="状态: approved/pending/rejected/stopped"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取所有学员排行榜"""
    # 生成缓存键
    # 添加版本号，确保代码修改后缓存会更新
    cache_key = f"leaderboard:v1:all:{current_user.id}:{order_by}:{limit}:{status}"
    from app.core.cache import cache
    
    # 尝试从缓存获取
    cached_result = await cache.get(cache_key)
    if cached_result:
        return cached_result
    
    leaderboard = await GrowthService.get_leaderboard(db, current_user.id, None, order_by, limit, status)
    
    # 处理排行榜数据
    result = []
    for rank, student in enumerate(leaderboard, 1):
        result.append({
            "rank": rank,
            "id": student["id"],
            "real_name": student["real_name"],
            "total_score": student["total_score"],
            "available_score": student["available_score"]
        })
    
    # 缓存结果，5分钟过期
    await cache.set(cache_key, result, expire=300)
    
    return result


@router.get("/classes")
async def get_classes_leaderboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取班级排行榜（按成长值排序）"""
    # 生成缓存键
    # 添加版本号，确保代码修改后缓存会更新
    cache_key = f"leaderboard:v1:classes:{current_user.id}"
    from app.core.cache import cache
    
    # 尝试从缓存获取
    cached_result = await cache.get(cache_key)
    if cached_result:
        return cached_result
    
    leaderboard = await GrowthService.get_class_leaderboard(db, current_user.id)
    
    result = {"items": leaderboard}
    
    # 缓存结果，5分钟过期
    await cache.set(cache_key, result, expire=300)
    
    return result
