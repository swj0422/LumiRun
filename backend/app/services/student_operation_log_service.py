import json
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.student_operation_log import StudentOperationLog
from app.core.database import AsyncSessionLocal
from app.core.logger import logger


class StudentOperationLogService:
    """学员操作日志服务类"""

    @staticmethod
    async def create_operation_log(
        operator_id: int,
        operator_name: str,
        class_id: int,
        class_student_id: int,
        class_name: str,
        student_name: str,
        operation_type: str,
        operation_content: str,
        before_data: dict = None,
        after_data: dict = None,
        ip_address: str = None
    ):
        """创建学员操作日志 - 使用独立事务，不影响主业务"""
        try:
            logger.info(f"[StudentOperationLog] Creating log: student={student_name}, type={operation_type}, content={operation_content}")
            async with AsyncSessionLocal() as log_db:
                # 转换字典为JSON字符串
                before_data_json = json.dumps(before_data, ensure_ascii=False) if before_data else None
                after_data_json = json.dumps(after_data, ensure_ascii=False) if after_data else None
                
                log = StudentOperationLog(
                    operator_id=operator_id,
                    operator_name=operator_name,
                    class_id=class_id,
                    class_student_id=class_student_id,
                    class_name=class_name if class_name else "未知班级",
                    student_name=student_name,
                    operation_type=operation_type,
                    operation_content=operation_content,
                    before_data=before_data_json,
                    after_data=after_data_json,
                    ip_address=ip_address
                )

                log_db.add(log)
                await log_db.commit()
                await log_db.refresh(log)
                logger.info(f"[StudentOperationLog] Log created successfully: id={log.id}")
                return log
        except Exception as e:
            logger.error(f"[StudentOperationLog] Failed to create log: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
