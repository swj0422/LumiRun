from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_user, require_teacher, require_growth_permission
from app.schemas.growth import GrowthLogCreate, GrowthLogResponse, GrowthScoreResponse, GrowthReasonCreate, GrowthReasonResponse
from app.services.growth_service import GrowthService
from app.models.user import User

router = APIRouter()


@router.post("/record", response_model=dict)
async def record_growth(
    log_data: GrowthLogCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """记录成长值变动"""
    # 检查权限
    has_permission, class_ids = await require_growth_permission(log_data.class_id, current_user, db)
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有权限操作此班级"
        )

    try:
        growth_log = await GrowthService.record_growth_log(db, log_data, current_user.id)

        return {
            "message": "成长值记录成功",
            "log_id": growth_log.id,
            "student_id": growth_log.class_student_id
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/logs", response_model=dict)
async def get_growth_logs(
    class_id: Optional[int] = Query(None, description="班级ID"),
    student_name: Optional[str] = Query(None, description="学员姓名"),
    school_name: Optional[str] = Query(None, description="学校名称"),
    session: Optional[str] = Query(None, description="届"),
    class_name: Optional[str] = Query(None, description="班级名称"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    change_type: Optional[str] = Query(None, description="变动类型: positive/negative"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    identity: Optional[str] = Query(None, description="身份：assistant（助理）或 student（学员）"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取成长值流水"""
    from app.core.permission import PermissionChecker

    # 检查权限
    is_teacher, assistant_class_ids = await PermissionChecker.require_growth_permission(
        db, current_user, class_id
    )

    # 根据身份参数决定显示什么记录
    # 如果 identity=assistant，只显示自己操作的记录
    # 如果 identity=student，只显示自己被加减的成长值
    # 如果没有指定身份，默认按原有逻辑处理
    if identity == "assistant":
        # 助理身份：只显示自己操作的记录
        logs, total = await GrowthService.get_growth_logs(
            db, current_user.id, start_time, end_time, change_type, skip, limit, class_id, student_name, school_name, session, class_name,
            only_own_records=True,
            assistant_class_ids=assistant_class_ids,
            force_assistant=True
        )
    elif identity == "student":
        # 学员身份：只显示自己被加减的成长值
        logs, total = await GrowthService.get_growth_logs(
            db, current_user.id, start_time, end_time, change_type, skip, limit, class_id, student_name, school_name, session, class_name,
            only_own_records=True,
            force_student=True
        )
    else:
        # 默认逻辑
        logs, total = await GrowthService.get_growth_logs(
            db, current_user.id, start_time, end_time, change_type, skip, limit, class_id, student_name, school_name, session, class_name,
            only_own_records=not is_teacher,
            assistant_class_ids=assistant_class_ids if not is_teacher else None
        )

    log_list = []
    for log in logs:
        log_list.append({
            "id": log["id"],
            "user_id": log["user_id"],
            "class_id": log["class_id"],
            "teacher_id": log["teacher_id"],
            "change_score": log["change_score"],
            "reason": log["reason"],
            "operator_id": log["operator_id"],
            "operator_name": log.get("operator_name", ""),
            "input_type": log["input_type"],
            "input_type_name": "手动录入" if log["input_type"] == 1 else "语音录入",
            "created_at": log["created_at"],
            "updated_at": log.get("updated_at"),
            "student_name": log.get("student_name", ""),
            "class_name": log.get("class_name", ""),
            "school_name": log.get("school_name", ""),
            "session": log.get("session", "")
        })

    return {
        "items": log_list,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/score", response_model=GrowthScoreResponse)
async def get_growth_score(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取成长值总额"""
    # 查找当前用户对应的ClassStudent记录
    from app.models.class_student import ClassStudent
    from app.models.student_profile import StudentProfile

    student_class_result = await db.execute(
        select(ClassStudent).join(
            StudentProfile, StudentProfile.id == ClassStudent.student_profile_id
        ).where(
            StudentProfile.user_id == current_user.id
        )
    )
    student_class = student_class_result.scalar_one_or_none()

    if not student_class:
        return {
            "user_id": current_user.id,
            "student_name": current_user.real_name,
            "total_score": 0,
            "available_score": 0
        }

    # 使用class_student.id作为唯一标识获取成长值
    growth_score = await GrowthService.get_growth_score(db, student_class.id)

    return {
        "user_id": current_user.id,
        "student_name": current_user.real_name,
        "total_score": growth_score["total_score"],
        "available_score": growth_score["available_score"]
    }


@router.get("/history", response_model=dict)
async def get_growth_history(
    start_time: Optional[str] = Query(None, description="开始时间"),
    end_time: Optional[str] = Query(None, description="结束时间"),
    student_name: Optional[str] = Query(None, description="学员姓名"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取成长值变更流水（所有操作，包括添加和删除）"""
    from datetime import datetime

    # 解析时间参数
    start_datetime = None
    if start_time:
        try:
            start_datetime = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        except ValueError:
            pass

    end_datetime = None
    if end_time:
        try:
            end_datetime = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        except ValueError:
            pass

    # 获取成长值变更流水
    history_data, total = await GrowthService.get_growth_history(
        db,
        current_user.id,
        start_time=start_datetime,
        end_time=end_datetime,
        student_name=student_name,
        skip=skip,
        limit=limit
    )

    return {
        "items": history_data,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.put("/logs/{log_id}", response_model=dict)
async def update_growth_log(
    log_id: int,
    update_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """修改成长值记录"""
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"接收到修改成长值记录请求: log_id={log_id}, update_data={update_data}, current_user.id={current_user.id}")
    try:
        change_score = update_data.get("change_score")
        reason = update_data.get("reason")

        logger.info(f"提取参数: change_score={change_score}, reason={reason}")

        if change_score is None or reason is None:
            logger.error("缺少必要的修改参数")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="缺少必要的修改参数"
            )

        # 确保change_score是整数类型
        try:
            change_score = int(change_score)
        except (ValueError, TypeError):
            logger.error("change_score必须是整数类型")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="成长值必须是整数"
            )

        logger.info("调用GrowthService.update_growth_log")
        updated_log = await GrowthService.update_growth_log(db, log_id, change_score, reason, current_user.id)
        logger.info("修改成功")
        return {
            "message": "修改成功",
            "log": {
                "id": updated_log.id,
                "class_student_id": updated_log.class_student_id,
                "class_id": updated_log.class_id,
                "user_id": updated_log.user_id,
                "change_value": updated_log.change_value,
                "reason": updated_log.reason,
                "operator_id": updated_log.operator_id,
                "input_type": updated_log.input_type,
                "created_at": updated_log.created_at,
                "updated_at": updated_log.updated_at
            }
        }
    except ValueError as e:
        logger.error(f"ValueError: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Exception: {e}")
        import traceback
        logger.error(f"错误堆栈: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="修改失败，请稍后重试"
        )


@router.get("/reasons", response_model=dict)
async def get_growth_reasons(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取成长原因列表"""
    from app.services.growth_service import GrowthService

    reasons = await GrowthService.get_growth_reasons(db, current_user.id)

    return {
        "items": reasons
    }


@router.post("/reasons", response_model=dict)
async def create_growth_reason(
    reason_data: GrowthReasonCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建成长原因"""
    try:
        reason = await GrowthService.create_growth_reason(db, reason_data, current_user.id)
        return {
            "message": "成长原因创建成功",
            "reason_id": reason.id
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/leaderboard/class/{class_id}", response_model=dict)
async def get_class_leaderboard(
    class_id: int,
    order_by: str = Query("total_score", description="排序字段: total_score/available_score"),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取班级排行榜"""
    leaderboard = await GrowthService.get_leaderboard(db, current_user.id, class_id, order_by, limit)
    return {
        "items": leaderboard
    }


@router.get("/leaderboard/all", response_model=dict)
async def get_all_leaderboard(
    order_by: str = Query("total_score", description="排序字段: total_score/available_score"),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取全部排行榜"""
    leaderboard = await GrowthService.get_leaderboard(db, current_user.id, None, order_by, limit)
    return {
        "items": leaderboard
    }


@router.get("/leaderboard/class", response_model=dict)
async def get_class_leaderboard_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取各班级排行榜汇总"""
    leaderboard = await GrowthService.get_class_leaderboard(db, current_user.id)
    return {
        "items": leaderboard
    }


@router.post("/batch-import", response_model=dict)
async def batch_import_growth_logs(
    records: List[GrowthLogCreate],
    current_user: User = Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """批量导入成长值记录（异步处理）"""
    # 这里直接返回成功，actual processing happens in background
    background_tasks.add_task(
        GrowthService.batch_import_growth_logs,
        records,
        current_user.id
    )

    return {
        "message": "批量导入任务已提交，请稍后查看结果"
    }


@router.get("/export", response_model=dict)
async def export_growth_logs(
    class_id: Optional[int] = Query(None, description="班级ID"),
    student_name: Optional[str] = Query(None, description="学员姓名"),
    school_name: Optional[str] = Query(None, description="学校名称"),
    session: Optional[str] = Query(None, description="届"),
    class_name: Optional[str] = Query(None, description="班级名称"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    change_type: Optional[str] = Query(None, description="变动类型: positive/negative"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """导出成长值记录"""
    from app.services.export_service import ExportService
    from app.core.security import require_teacher

    # 检查权限
    is_teacher_user = current_user.role.role_name in ["super_admin", "admin", "teacher"]
    if not is_teacher_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有导师可以导出成长值记录"
        )

    try:
        # 获取成长值记录
        logs, total = await GrowthService.get_growth_logs(
            db, current_user.id, start_time, end_time, change_type, 0, 10000, class_id,
            student_name, school_name, session, class_name
        )

        # 生成导出数据
        export_data = []
        for log in logs:
            export_data.append({
                "学员姓名": log.get("student_name", ""),
                "班级": log.get("class_name", ""),
                "学校": log.get("school_name", ""),
                "成长值": log.get("change_score", 0),
                "原因": log.get("reason", ""),
                "操作人": log.get("operator_name", ""),
                "时间": log.get("created_at", "")
            })

        return {
            "items": export_data,
            "total": len(export_data)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导出失败: {str(e)}"
        )
