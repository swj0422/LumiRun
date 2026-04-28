import csv
import io
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.growth_log import Growth
from app.models.class_student import ClassStudent
from app.models.gift_order import GiftOrder
from app.models.system_log import SystemLog
from app.models.user import User
from app.models.class_info import ClassInfo
from app.models.student_profile import StudentProfile
from app.core.logger import logger


class ExportService:
    """数据导出服务"""
    
    @staticmethod
    async def export_growth_records(
        db: AsyncSession,
        teacher_id: int,
        class_id: Optional[int] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> io.StringIO:
        """导出成长值流水记录"""
        # 获取导师的班级
        classes = await db.execute(
            select(ClassInfo.id).where(ClassInfo.teacher_id == teacher_id)
        )
        class_ids = [c[0] for c in classes.all()]
        
        if not class_ids:
            raise ValueError("您没有创建任何班级")
        
        # 构建查询条件
        query = select(
            Growth.id,
            ClassInfo.class_name,
            ClassStudent.name_in_class,
            User.real_name.label("teacher_name"),
            Growth.change_value,
            Growth.reason,
            Growth.created_at
        ).join(
            ClassInfo, ClassInfo.id == Growth.class_id
        ).join(
            ClassStudent, ClassStudent.id == Growth.class_student_id
        ).join(
            User, User.id == Growth.operator_id
        ).where(
            Growth.class_id.in_(class_ids)
        )
        
        if class_id:
            query = query.where(Growth.class_id == class_id)
        if start_time:
            query = query.where(Growth.created_at >= start_time)
        if end_time:
            query = query.where(Growth.created_at <= end_time)
        
        result = await db.execute(query)
        records = result.all()
        
        # 创建 CSV 文件
        output = io.StringIO()
        writer = csv.writer(output)
        
        # 写入表头
        writer.writerow(["流水ID", "班级名称", "学员姓名", "操作导师", "变动数值", "变动原因", "变动时间"])
        
        # 写入数据
        for record in records:
            writer.writerow([
                record[0],
                record[1],
                record[2],
                record[3],
                record[4],
                record[5],
                record[6].strftime("%Y-%m-%d %H:%M:%S")
            ])
        
        output.seek(0)
        return output
    
    @staticmethod
    async def export_class_students(
        db: AsyncSession,
        teacher_id: int,
        class_id: Optional[int] = None
    ) -> io.StringIO:
        """导出学员-班级绑定记录"""
        # 获取导师的班级
        classes = await db.execute(
            select(ClassInfo.id).where(ClassInfo.teacher_id == teacher_id)
        )
        class_ids = [c[0] for c in classes.all()]
        
        if not class_ids:
            raise ValueError("您没有创建任何班级")
        
        # 构建查询条件
        query = select(
            ClassStudent.id,
            ClassInfo.class_name,
            ClassStudent.name_in_class,
            ClassStudent.student_no_in_class,
            StudentProfile.real_name.label("profile_real_name"),
            User.username,
            ClassStudent.bind_status,
            ClassStudent.bind_time,
            ClassStudent.remove_reason,
            ClassStudent.created_at
        ).join(
            ClassInfo, ClassInfo.id == ClassStudent.class_id
        ).outerjoin(
            StudentProfile, StudentProfile.id == ClassStudent.student_profile_id
        ).outerjoin(
            User, User.id == StudentProfile.user_id
        ).where(
            ClassStudent.class_id.in_(class_ids)
        )
        
        if class_id:
            query = query.where(ClassStudent.class_id == class_id)
        
        result = await db.execute(query)
        records = result.all()
        
        # 创建 CSV 文件
        output = io.StringIO()
        writer = csv.writer(output)
        
        # 写入表头
        writer.writerow(["绑定ID", "班级名称", "班内姓名", "班内学号", "真实姓名", "用户名", "绑定状态", "绑定时间", "解绑原因", "创建时间"])
        
        # 写入数据
        for record in records:
            writer.writerow([
                record[0],
                record[1],
                record[2],
                record[3],
                record[4] or "",
                record[5] or "",
                "待审核" if record[6] == "pending" else "已通过" if record[6] == "approved" else "已拒绝" if record[6] == "rejected" else "已停用" if record[6] == "stopped" else "已解除",
                record[7].strftime("%Y-%m-%d %H:%M:%S") if record[7] else "",
                record[8] or "",
                record[9].strftime("%Y-%m-%d %H:%M:%S")
            ])
        
        output.seek(0)
        return output
    
    @staticmethod
    async def export_gift_orders(
        db: AsyncSession,
        teacher_id: int,
        class_id: Optional[int] = None,
        status: Optional[int] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> io.StringIO:
        """导出奖励兑换订单"""
        # 获取导师的班级
        classes = await db.execute(
            select(ClassInfo.id).where(ClassInfo.teacher_id == teacher_id)
        )
        class_ids = [c[0] for c in classes.all()]
        
        if not class_ids:
            raise ValueError("您没有创建任何班级")
        
        # 构建查询条件
        query = select(
            GiftOrder.id,
            ClassInfo.class_name,
            User.real_name.label("student_name"),
            GiftOrder.gift_id,
            GiftOrder.cost_score,
            GiftOrder.status,
            GiftOrder.cancel_reason,
            GiftOrder.created_at,
            GiftOrder.updated_at
        ).join(
            ClassInfo, ClassInfo.id == GiftOrder.class_id
        ).join(
            ClassStudent, ClassStudent.id == GiftOrder.class_student_id
        ).join(
            User, User.id == ClassStudent.user_id
        ).where(
            GiftOrder.class_id.in_(class_ids)
        )
        
        if class_id:
            query = query.where(GiftOrder.class_id == class_id)
        if status is not None:
            query = query.where(GiftOrder.status == status)
        if start_time:
            query = query.where(GiftOrder.created_at >= start_time)
        if end_time:
            query = query.where(GiftOrder.created_at <= end_time)
        
        result = await db.execute(query)
        records = result.all()
        
        # 创建 CSV 文件
        output = io.StringIO()
        writer = csv.writer(output)
        
        # 写入表头
        writer.writerow(["订单ID", "班级名称", "学员姓名", "礼品ID", "消耗成长值", "订单状态", "取消原因", "创建时间", "更新时间"])
        
        # 写入数据
        for record in records:
            writer.writerow([
                record[0],
                record[1],
                record[2],
                record[3],
                record[4],
                "待核销" if record[5] == 0 else "已核销" if record[5] == 1 else "已取消",
                record[6] or "",
                record[7].strftime("%Y-%m-%d %H:%M:%S"),
                record[8].strftime("%Y-%m-%d %H:%M:%S")
            ])
        
        output.seek(0)
        return output
    
    @staticmethod
    async def export_system_logs(
        db: AsyncSession,
        user_id: Optional[int] = None,
        log_type: Optional[str] = None,
        log_level: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> io.StringIO:
        """导出系统日志"""
        # 构建查询条件
        query = select(
            SystemLog.id,
            SystemLog.user_id,
            SystemLog.username,
            SystemLog.real_name,
            SystemLog.log_type,
            SystemLog.log_level,
            SystemLog.module,
            SystemLog.action,
            SystemLog.ip_address,
            SystemLog.request_url,
            SystemLog.request_method,
            SystemLog.response_status,
            SystemLog.error_message,
            SystemLog.created_at
        )
        
        if user_id:
            query = query.where(SystemLog.user_id == user_id)
        if log_type:
            query = query.where(SystemLog.log_type == log_type)
        if log_level:
            query = query.where(SystemLog.log_level == log_level)
        if start_time:
            query = query.where(SystemLog.created_at >= start_time)
        if end_time:
            query = query.where(SystemLog.created_at <= end_time)
        
        result = await db.execute(query)
        records = result.all()
        
        # 创建 CSV 文件
        output = io.StringIO()
        writer = csv.writer(output)
        
        # 写入表头
        writer.writerow(["日志ID", "用户ID", "用户名", "真实姓名", "日志类型", "日志级别", "模块", "动作", "IP地址", "请求URL", "请求方法", "响应状态", "错误信息", "创建时间"])
        
        # 写入数据
        for record in records:
            writer.writerow([
                record[0],
                record[1] or "",
                record[2] or "",
                record[3] or "",
                record[4],
                record[5],
                record[6],
                record[7],
                record[8] or "",
                record[9] or "",
                record[10] or "",
                record[11] or "",
                record[12] or "",
                record[13].strftime("%Y-%m-%d %H:%M:%S")
            ])
        
        output.seek(0)
        return output
