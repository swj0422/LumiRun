from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.core.database import get_db
from app.core.security import get_current_user, require_teacher
from app.models.wish import Wish
from app.models.gift import Gift
from app.models.user import User
from app.services.wish_service import WishService
from pydantic import BaseModel, Field

router = APIRouter()


class WishCreate(BaseModel):
    gift_id: int = Field(..., description="礼品ID")
    class_id: int = Field(..., description="班级ID")


@router.post("/")
async def create_wish(
    wish_data: WishCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建学员心愿"""
    try:
        wish = await WishService.create_wish(
            db=db,
            user_id=current_user.id,
            gift_id=wish_data.gift_id,
            class_id=wish_data.class_id
        )
        
        # 获取礼品信息
        gift = await db.execute(
            select(Gift).where(Gift.id == wish.gift_id)
        )
        gift = gift.scalar_one_or_none()
        
        return {
            "id": wish.id,
            "gift_id": wish.gift_id,
            "gift_name": gift.name if gift else "",
            "class_id": wish.class_id,
            "status": wish.status,
            "created_at": wish.created_at
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/user")
async def get_user_wishes(
    status: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取学员的心愿列表"""
    wishes, total = await WishService.get_user_wishes(
        db=db,
        user_id=current_user.id,
        status=status,
        skip=skip,
        limit=limit
    )
    
    wish_list = []
    for wish in wishes:
        gift = await db.execute(
            select(Gift).where(Gift.id == wish.gift_id)
        )
        gift = gift.scalar_one_or_none()
        
        wish_list.append({
            "id": wish.id,
            "gift_id": wish.gift_id,
            "gift_name": gift.name if gift else "",
            "gift_price": gift.cost_score if gift else 0,
            "gift_stock": gift.stock.current_stock if gift and hasattr(gift, 'stock') else 0,
            "class_id": wish.class_id,
            "status": wish.status,
            "status_text": "未处理" if wish.status else "已处理",
            "notified_at": wish.notified_at,
            "created_at": wish.created_at
        })
    
    return {
        "items": wish_list,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/teacher")
async def get_class_wishes(
    class_id: Optional[int] = Query(None),
    status: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    """获取导师班级的心愿列表"""
    wishes, total = await WishService.get_class_wishes(
        db=db,
        teacher_id=current_user.id,
        class_id=class_id,
        status=status,
        skip=skip,
        limit=limit
    )
    
    wish_list = []
    for wish in wishes:
        gift = await db.execute(
            select(Gift).where(Gift.id == wish.gift_id)
        )
        gift = gift.scalar_one_or_none()
        
        user = await db.execute(
            select(User).where(User.id == wish.user_id)
        )
        user = user.scalar_one_or_none()
        
        wish_list.append({
            "id": wish.id,
            "user_id": wish.user_id,
            "user_name": user.real_name if user else "",
            "gift_id": wish.gift_id,
            "gift_name": gift.name if gift else "",
            "gift_price": gift.cost_score if gift else 0,
            "class_id": wish.class_id,
            "status": wish.status,
            "status_text": "未处理" if wish.status else "已处理",
            "notified_at": wish.notified_at,
            "created_at": wish.created_at
        })
    
    return {
        "items": wish_list,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.delete("/{wish_id}")
async def delete_wish(
    wish_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除学员心愿"""
    success = await WishService.delete_wish(
        db=db,
        wish_id=wish_id,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="心愿不存在"
        )
    
    return {
        "message": "删除成功"
    }


@router.post("/process")
async def process_wishes(
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    """处理心愿（库存通知）"""
    processed_count = await WishService.process_wishes(db=db)
    
    return {
        "message": "处理完成",
        "processed_count": processed_count
    }
