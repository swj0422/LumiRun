from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from app.core.database import get_db
from app.core.security import require_admin
from app.models.user import User
from app.models.gift import Gift
from app.models.gift_stock import GiftStock

router = APIRouter()


@router.get("/gifts")
async def get_admin_gifts(
    name: Optional[str] = Query(None, description="礼品名称"),
    status: Optional[int] = Query(None, description="礼品状态"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    query = select(Gift)
    
    if name:
        query = query.where(Gift.name.contains(name))
    if status is not None:
        query = query.where(Gift.status == status)
    if keyword:
        query = query.where(Gift.name.contains(keyword))
    
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0
    
    query = query.order_by(Gift.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    gifts = result.scalars().all()
    
    gift_list = []
    for gift in gifts:
        stock_result = await db.execute(select(GiftStock).where(GiftStock.gift_id == gift.id))
        stock = stock_result.scalar_one_or_none()
        
        stock_info = {
            "id": stock.id,
            "gift_id": stock.gift_id,
            "current_stock": stock.current_stock,
            "total_in_stock": stock.total_in_stock,
            "total_out_stock": stock.total_out_stock,
            "updated_at": stock.updated_at
        } if stock else {}
        
        teacher_result = await db.execute(select(User).where(User.id == gift.teacher_id))
        teacher = teacher_result.scalar_one_or_none()
        creator_name = teacher.real_name if teacher else "-"
        
        gift_list.append({
            "id": gift.id,
            "name": gift.name,
            "description": gift.description,
            "price": gift.price,
            "stock": stock_info,
            "status": gift.status,
            "image_url": gift.image_url,
            "created_at": gift.created_at,
            "updated_at": gift.updated_at,
            "creator_name": creator_name
        })
    
    return {
        "items": gift_list,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/gifts/{gift_id}")
async def get_gift_detail(
    gift_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    gift = await db.get(Gift, gift_id)
    
    if not gift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="礼品不存在"
        )
    
    stock_result = await db.execute(select(GiftStock).where(GiftStock.gift_id == gift.id))
    stock = stock_result.scalar_one_or_none()
    
    stock_info = {
        "id": stock.id,
        "gift_id": stock.gift_id,
        "current_stock": stock.current_stock,
        "total_in_stock": stock.total_in_stock,
        "total_out_stock": stock.total_out_stock,
        "updated_at": stock.updated_at
    } if stock else {}
    
    return {
        "id": gift.id,
        "name": gift.name,
        "description": gift.description,
        "price": gift.price,
        "stock": stock_info,
        "status": gift.status,
        "image_url": gift.image_url,
        "created_at": gift.created_at,
        "updated_at": gift.updated_at
    }


@router.delete("/gifts/{gift_id}")
async def delete_gift(
    gift_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    from sqlalchemy import text
    from app.models.system_log import SystemLog, LogType, LogLevel
    
    gift = await db.get(Gift, gift_id)
    if not gift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="礼品不存在"
        )
    
    gift_name = gift.name
    
    stock_result = await db.execute(select(GiftStock).where(GiftStock.gift_id == gift.id))
    stock = stock_result.scalar_one_or_none()
    stock_info = f'{{"current_stock": {stock.current_stock}}}' if stock else '{}'
    
    await db.execute(text("DELETE FROM gift_order WHERE gift_id = :gift_id"), {"gift_id": gift_id})
    await db.execute(text("DELETE FROM gift_order_log WHERE gift_id = :gift_id"), {"gift_id": gift_id})
    
    await db.delete(gift)
    
    system_log = SystemLog(
        user_id=current_user.id,
        username=current_user.username,
        real_name=current_user.real_name,
        log_type=LogType.DELETE,
        log_level=LogLevel.INFO,
        module="礼品管理",
        action="删除礼品",
        biz_type="gift",
        biz_id=gift_id,
        request_params=f'{{"gift_id": {gift_id}}}',
        before_data=f'{{"礼品名称": "{gift_name}", "价格": {gift.price}, "库存": {stock_info}}}'
    )
    db.add(system_log)
    
    await db.commit()
    
    return {"message": "删除成功"}
