from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_user, require_teacher, require_admin
from app.models.user import User
from app.services.export_service import ExportService

router = APIRouter()


@router.get("/growth-records")
async def export_growth_records(
    class_id: Optional[int] = Query(None),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    """导出成长值流水记录"""
    try:
        output = await ExportService.export_growth_records(
            db=db,
            teacher_id=current_user.id,
            class_id=class_id,
            start_time=start_time,
            end_time=end_time
        )
        
        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=growth_records_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.csv"
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/class-students")
async def export_class_students(
    class_id: Optional[int] = Query(None),
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    """导出学员-班级绑定记录"""
    try:
        output = await ExportService.export_class_students(
            db=db,
            teacher_id=current_user.id,
            class_id=class_id
        )
        
        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=class_students_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.csv"
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/gift-orders")
async def export_gift_orders(
    class_id: Optional[int] = Query(None),
    status: Optional[int] = Query(None),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db)
):
    """导出奖励兑换订单"""
    try:
        output = await ExportService.export_gift_orders(
            db=db,
            teacher_id=current_user.id,
            class_id=class_id,
            status=status,
            start_time=start_time,
            end_time=end_time
        )
        
        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=gift_orders_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.csv"
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/system-logs")
async def export_system_logs(
    user_id: Optional[int] = Query(None),
    log_type: Optional[str] = Query(None),
    log_level: Optional[str] = Query(None),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """导出系统日志（管理员）"""
    try:
        output = await ExportService.export_system_logs(
            db=db,
            user_id=user_id,
            log_type=log_type,
            log_level=log_level,
            start_time=start_time,
            end_time=end_time
        )
        
        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=system_logs_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.csv"
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
