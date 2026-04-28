from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from app.models.class_student import ClassStudent, BindStatus
from app.models.class_info import ClassInfo
from app.models.growth_log import Growth

from app.models.student_profile import StudentProfile
from app.schemas.growth import GrowthLogCreate
from app.core.logger import logger


class GrowthService:
    @staticmethod
    async def record_growth_log(
        db: AsyncSession,
        log_data: GrowthLogCreate,
        teacher_id: int
    ) -> Growth:
        """记录成长值变动"""
        # 查找学员
        student = await GrowthService._search_students(db, teacher_id, log_data.student_name, None, log_data.class_id)
        if not student:
            raise ValueError("学员不存在")

        # 检查班级状态
        from sqlalchemy.orm import selectinload
        class_info = await db.execute(
            select(ClassInfo).options(selectinload(ClassInfo.teacher)).where(ClassInfo.id == student.class_id)
        )
        class_info = class_info.scalars().first()
        if not class_info or not class_info.status:
            raise ValueError("班级不存在或已关闭")

        # 移除绑定状态检查，所有学生都可以记录成长值
        # if student.bind_status != BindStatus.APPROVED:
        #     raise ValueError("学员状态异常，无法记录成长值")

        # 计算当前成长值
        from sqlalchemy import func
        result = await db.execute(
            select(func.sum(Growth.change_value))
            .where(Growth.class_student_id == student.id)
        )
        current_score = result.scalar() or 0
        new_score = current_score + log_data.change_score

        # 记录成长值变动
        # 对于有student_profile_id的学员，通过student_profile获取user_id
        # 对于没有student_profile_id的学员（导师直接导入的），user_id设为None
        user_id = None
        if student.student_profile:
            user_id = student.student_profile.user_id

        growth = Growth(
            user_id=user_id,
            class_student_id=student.id,
            class_id=student.class_id,
            teacher_id=teacher_id,
            change_value=log_data.change_score,
            reason=log_data.reason,
            operator_id=teacher_id,
            input_type=int(log_data.input_type),
            class_status=class_info.status
        )

        db.add(growth)

        # 提交事务以获取growth的ID
        await db.flush()

        # 创建成长值操作日志记录（不可变）
        from app.models.growth_journal import GrowthOperationLog
        # 获取操作人姓名
        from app.models.user import User
        operator = await db.get(User, teacher_id)
        operator_name = operator.real_name if operator else "未知用户"
        growth_operation_log = GrowthOperationLog(
            student_name=log_data.student_name,
            class_name=class_info.class_name,
            teacher_name=class_info.teacher.real_name if class_info.teacher else "未知导师",
            operator_name=operator_name,
            old_value=current_score,
            new_value=new_score,
            change_value=log_data.change_score,
            reason=log_data.reason,
            operation_type="add"
        )
        db.add(growth_operation_log)

        # 不再使用GrowthScore表存储成长值总额，直接从Growth表计算
        # 移除更新GrowthScore的逻辑

        # 记录系统日志
        from app.models.user import User
        from app.models.system_log import SystemLog, LogType, LogLevel

        # 获取操作用户信息
        operator = await db.get(User, teacher_id)
        operator_name = operator.real_name if operator else "未知用户"

        # 记录系统日志
        system_log = SystemLog(
            user_id=teacher_id,
            username=operator.username if operator else "",
            real_name=operator_name,
            log_type=LogType.CREATE,
            log_level=LogLevel.INFO,
            module="成长值管理",
            action="添加成长值记录",
            request_params=f"{{\"student_name\": \"{log_data.student_name}\", \"change_score\": {log_data.change_score}, \"reason\": \"{log_data.reason}\"}}"
        )
        db.add(system_log)

        try:
            await db.commit()
            await db.refresh(growth)
            logger.info(f"成长值记录: 学员{growth.class_student_id}, 变动{log_data.change_score}, 原因{log_data.reason}")

            # 清除相关缓存
            from app.core.cache import cache
            await cache.clear_pattern(f"leaderboard:*:{teacher_id}:*")
            await cache.clear_pattern(f"leaderboard:all:{teacher_id}:*")
            await cache.clear_pattern(f"leaderboard:classes:{teacher_id}")
            # 清除成长值缓存
            if user_id:
                await cache.clear_pattern(f"growth_score:{user_id}")
            # 清除班级学员的成长值缓存
            await cache.clear_pattern(f"growth_score:{student.id}")
            # 清除成长值日志缓存
            await cache.clear_pattern(f"growth_logs:*")

            return growth
        except Exception as e:
            await db.rollback()
            logger.error(f"记录成长值失败: {e}")
            raise

    @staticmethod
    async def _search_students(db: AsyncSession, user_id: int, student_name: str, student_no: Optional[str] = None, class_id: Optional[int] = None) -> Optional[ClassStudent]:
        """搜索学员"""
        # 首先获取用户的所有班级（包括导师的班级和班级助理被授权的班级）
        from app.services.class_assistant_service import ClassAssistantService
        from app.models.user import User
        from sqlalchemy import or_

        # 获取用户信息
        user = await db.get(User, user_id)
        if not user:
            return None

        # 确定用户类型
        is_teacher = user.role.role_name in ["super_admin", "admin", "teacher"]

        class_ids = []

        if is_teacher:
            # 对于导师，获取其所有班级
            classes = await db.execute(
                select(ClassInfo.id).where(ClassInfo.teacher_id == user_id)
            )
            class_ids = classes.scalars().all()
        else:
            # 对于班级助理，获取其被授权的班级
            assistant_classes = await ClassAssistantService.get_user_assistant_classes(db, user_id)
            class_ids = [cls.id for cls in assistant_classes]

        # 如果指定了班级ID，且该班级在用户的班级列表中，则只搜索该班级
        if class_id and class_id in class_ids:
            class_ids = [class_id]
        elif class_id:
            # 如果指定了班级ID，但该班级不在用户的班级列表中，则返回None
            return None

        if not class_ids:
            return None

        # 搜索班级学员，预加载student_profile关系，过滤已删除学员
        from sqlalchemy.orm import selectinload
        # 构建查询条件
        conditions = [
            ClassStudent.class_id.in_(class_ids),
            ClassStudent.is_deleted == False
        ]

        # 如果提供了学号，优先通过学号搜索
        if student_no:
            conditions.append(ClassStudent.student_no_in_class == student_no)
        else:
            # 否则通过姓名搜索
            conditions.append(
                or_(
                    ClassStudent.name_in_class.contains(student_name),
                    ClassStudent.student_profile.has(StudentProfile.real_name.contains(student_name)) if StudentProfile else ClassStudent.name_in_class.contains(student_name)
                )
            )

        result = await db.execute(
            select(ClassStudent).options(selectinload(ClassStudent.student_profile)).where(
                *conditions
            ).order_by(
                ClassStudent.name_in_class
            )
        )

        return result.scalars().first()

    @staticmethod
    async def get_leaderboard(
        db: AsyncSession,
        teacher_id: int,
        class_id: Optional[int] = None,
        order_by: str = 'total_score',
        limit: int = 10,
        status: Optional[str] = None
    ) -> List[dict]:
        """获取排行榜"""
        from app.core.logger import logger
        import time
        start_time = time.time()
        logger.info(f"[DEBUG] get_leaderboard called with teacher_id: {teacher_id}, class_id: {class_id}, order_by: {order_by}, limit: {limit}, status: {status}")

        try:
            # 尝试从缓存获取
            from app.core.cache import cache
            # 添加版本号，确保代码修改后缓存会更新
            if class_id:
                cache_key = f"leaderboard:v3:class:{teacher_id}:{class_id}:{order_by}:{limit}:{status}"
            else:
                cache_key = f"leaderboard:v3:all:{teacher_id}:{order_by}:{limit}:{status}"
            cached_result = await cache.get(cache_key)
            if cached_result:
                logger.info(f"[DEBUG] Leaderboard cache hit, time: {time.time() - start_time:.4f}s")
                return cached_result

            # 获取当前用户的班级（导师自己的班级或班级助理被授权的班级）
            from app.services.class_assistant_service import ClassAssistantService

            # 检查用户是否是超级管理员
            from app.models.user import User
            user = await db.get(User, teacher_id)
            is_super_admin = user.role and user.role.role_name == "super_admin"
            logger.info(f"[DEBUG] Is super admin: {is_super_admin}")

            # 先获取用户作为导师的班级
            teacher_class_query = select(ClassInfo.id).where(ClassInfo.teacher_id == teacher_id)
            if class_id:
                teacher_class_query = teacher_class_query.where(ClassInfo.id == class_id)

            # 执行导师班级查询
            teacher_classes = await db.execute(teacher_class_query)
            teacher_class_ids = [c[0] for c in teacher_classes.all()]
            logger.info(f"[DEBUG] Teacher classes: {teacher_class_ids}")

            # 获取用户作为班级助理被授权的班级
            assistant_classes = await ClassAssistantService.get_user_assistant_classes(db, teacher_id)
            assistant_class_ids = [cls.id for cls in assistant_classes]
            logger.info(f"[DEBUG] Assistant classes: {assistant_class_ids}")

            # 合并班级ID，去重
            all_class_ids = list(set(teacher_class_ids + assistant_class_ids))
            logger.info(f"[DEBUG] All classes: {all_class_ids}")

            # 如果是超级管理员，且没有指定班级ID，获取所有班级
            if is_super_admin and not class_id:
                all_classes = await db.execute(select(ClassInfo.id))
                all_class_ids = [c[0] for c in all_classes.all()]
                logger.info(f"[DEBUG] Super admin: All classes: {all_class_ids}")
            # 如果指定了班级ID，且是超级管理员，直接使用该班级ID
            elif is_super_admin and class_id:
                all_class_ids = [class_id]
                logger.info(f"[DEBUG] Super admin: Using class: {all_class_ids}")
            # 如果指定了班级ID，确保它在合并后的列表中
            elif class_id:
                if class_id not in all_class_ids:
                    logger.info(f"[DEBUG] Class {class_id} not in all_class_ids: {all_class_ids}")
                    return []
                all_class_ids = [class_id]
                logger.info(f"[DEBUG] Filtered to class: {all_class_ids}")

            if not all_class_ids:
                logger.info("[DEBUG] No classes found")
                return []

            class_ids = all_class_ids

            # 获取班级学员，与学员管理的过滤逻辑一致
            from sqlalchemy.orm import selectinload
            from app.models.class_student import BindStatus
            query = select(ClassStudent).options(
                selectinload(ClassStudent.class_info),
                selectinload(ClassStudent.student_profile)
            ).where(
                ClassStudent.class_id.in_(class_ids),
                ClassStudent.is_deleted == False
            )

            # 状态过滤（与学员管理逻辑一致）
            if status:
                if status == 'approved':
                    query = query.where(ClassStudent.bind_status == BindStatus.APPROVED)
                elif status == 'pending':
                    query = query.where(ClassStudent.bind_status == BindStatus.PENDING)
                elif status == 'rejected':
                    query = query.where(ClassStudent.bind_status == BindStatus.REJECTED)
                elif status == 'stopped':
                    query = query.where(ClassStudent.is_active == False)
                elif status == 'active':
                    query = query.where(ClassStudent.is_active == True)
            else:
                # 默认显示已通过和未绑定且未停用的学员
                query = query.where(
                    ClassStudent.bind_status.in_([BindStatus.APPROVED, BindStatus.NONE]),
                    ClassStudent.is_active == True
                )

            result = await db.execute(query)
            students = result.scalars().all()
            logger.info(f"[DEBUG] Found {len(students)} students")

            # 批量获取成长值，避免N+1查询
            student_ids = [student.id for student in students]
            logger.info(f"[DEBUG] Student IDs: {student_ids}")
            growth_scores = await GrowthService._get_batch_growth_scores(db, student_ids)
            logger.info(f"[DEBUG] Growth scores: {growth_scores}")

            # 构建排行榜数据
            leaderboard = []
            for student in students:
                # 从批量结果中获取成长值
                scores = growth_scores.get(student.id, {'total_score': 0, 'available_score': 0})
                total_score = scores['total_score']
                available_score = scores['available_score']

                # 处理学员姓名，确保不为空
                student_name = student.name_in_class
                if not student_name or student_name == '??':
                    # 如果没有班级内姓名，尝试使用学员档案的真实姓名
                    if student.student_profile and student.student_profile.real_name:
                        student_name = student.student_profile.real_name
                    else:
                        # 跳过使用默认名称的学员，只显示实际添加的学员
                        continue

                # 检查是否是当前用户
                is_current_user = False
                if student.student_profile and student.student_profile.user_id == teacher_id:
                    is_current_user = True
                    logger.info(f"[DEBUG] Current user found: {student_name}, total_score: {total_score}")
                
                # 显示总成长值不等于0的学员，或者是当前用户（即使总成长值为0）
                if total_score != 0 or is_current_user:
                    leaderboard.append({
                        "id": student.id,
                        "real_name": student_name,
                        "class_name": student.class_info.class_name if student.class_info else "未知班级",
                        "total_score": total_score,  # 不包括兑换记录的总和
                        "available_score": available_score,  # 包括兑换记录的扣除
                        "is_current_user": is_current_user,
                        "student_no_in_class": student.student_no_in_class
                    })

            logger.info(f"[DEBUG] Leaderboard before sort: {leaderboard}")

            # 排序
            if order_by == 'total_score':
                leaderboard.sort(key=lambda x: x['total_score'], reverse=True)
            elif order_by == 'available_score':
                leaderboard.sort(key=lambda x: x['available_score'], reverse=True)

            logger.info(f"[DEBUG] Leaderboard after sort: {leaderboard}")

            # 限制数量
            result = leaderboard[:limit]
            logger.info(f"[DEBUG] Leaderboard after limit: {result}")

            # 缓存结果，有效期5分钟
            await cache.set(cache_key, result, expire=300)
            logger.info(f"[DEBUG] Leaderboard cache set, time: {time.time() - start_time:.4f}s")

            return result
        except Exception as e:
            logger.error(f"获取排行榜失败: {e}")
            import traceback
            logger.error(f"错误堆栈: {traceback.format_exc()}")
            return []

    @staticmethod
    async def _get_batch_growth_scores(db: AsyncSession, student_ids: List[int]) -> Dict[int, Dict[str, int]]:
        """批量获取学员成长值，避免N+1查询"""
        from sqlalchemy import func, case
        import time
        start_time = time.time()

        # 计算总成长值（不包括兑换记录）
        total_score_query = select(
            Growth.class_student_id,
            func.sum(Growth.change_value).label('total_score')
        ).where(
            Growth.class_student_id.in_(student_ids),
            ~Growth.reason.like('%兑换%')  # 排除兑换记录
        ).group_by(Growth.class_student_id)

        # 计算可用成长值（包括兑换记录的扣除）
        available_score_query = select(
            Growth.class_student_id,
            func.sum(Growth.change_value).label('available_score')
        ).where(
            Growth.class_student_id.in_(student_ids)
        ).group_by(Growth.class_student_id)

        # 执行查询
        total_score_result = await db.execute(total_score_query)
        available_score_result = await db.execute(available_score_query)

        # 构建结果字典
        total_scores = {row[0]: int(row[1] or 0) for row in total_score_result.all()}
        available_scores = {row[0]: int(row[1] or 0) for row in available_score_result.all()}

        # 合并结果
        result = {}
        for student_id in student_ids:
            result[student_id] = {
                'total_score': total_scores.get(student_id, 0),
                'available_score': available_scores.get(student_id, 0)
            }

        return result

    @staticmethod
    async def get_growth_score(db: AsyncSession, user_id: int) -> Optional[dict]:
        """获取学员的成长值"""
        from app.core.logger import logger
        import time
        start_time = time.time()

        # 尝试从缓存获取
        from app.core.cache import cache
        cache_key = f"growth_score:{user_id}"
        cached_result = await cache.get(cache_key)
        if cached_result:
            logger.info(f"[DEBUG] Growth score cache hit, time: {time.time() - start_time:.4f}s")
            return cached_result

        # 从Growth表计算成长值，使用class_student.id作为唯一标识
        # 这里我们假设传入的user_id是class_student.id
        # 排除兑换记录，只计算通过成长管理增减的记录
        from sqlalchemy import func
        growth_query = select(func.sum(Growth.change_value)).where(
            Growth.class_student_id == user_id,
            ~Growth.reason.like('%兑换%')  # 排除兑换记录
        )
        growth_result = await db.execute(growth_query)
        total_score = growth_result.scalar() or 0
        # 转换为整数类型，避免Decimal序列化错误
        total_score = int(total_score)

        # 计算可用成长值（包括兑换记录的扣除）
        available_score_query = select(func.sum(Growth.change_value)).where(
            Growth.class_student_id == user_id
        )
        available_score_result = await db.execute(available_score_query)
        available_score = available_score_result.scalar() or 0
        available_score = int(available_score)

        # 返回一个字典，模拟GrowthScore对象的结构
        result = {
            "user_id": None,  # 不再使用user_id作为唯一标识
            "total_score": total_score,  # 不包括兑换记录的总和
            "available_score": available_score  # 包括兑换记录的扣除
        }

        # 缓存结果，有效期5分钟
        await cache.set(cache_key, result, expire=300)
        logger.info(f"[DEBUG] Growth score cache set, time: {time.time() - start_time:.4f}s")

        return result

    @staticmethod
    async def get_growth_logs(
        db: AsyncSession,
        teacher_id: int,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        change_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
        class_id: Optional[int] = None,
        student_name: Optional[str] = None,
        school_name: Optional[str] = None,
        session: Optional[str] = None,
        class_name: Optional[str] = None,
        only_own_records: bool = False,
        assistant_class_ids: Optional[List[int]] = None,
        force_assistant: bool = False,
        force_student: bool = False
    ) -> tuple[List[Dict[str, Any]], int]:
        """获取成长值流水"""
        from app.core.logger import logger
        import time
        start_time_ = time.time()

        try:
            # 尝试从缓存获取
            from app.core.cache import cache
            cache_key = f"growth_logs:{teacher_id}:{class_id or 'all'}:{student_name or 'none'}:{school_name or 'none'}:{session or 'none'}:{class_name or 'none'}:{start_time or 'none'}:{end_time or 'none'}:{change_type or 'none'}:{skip}:{limit}:{only_own_records}"
            cached_result = await cache.get(cache_key)
            if cached_result:
                logger.info(f"[DEBUG] Growth logs cache hit, time: {time.time() - start_time_:.4f}s")
                return cached_result

            # 检查用户是否是学员
            from app.models.student_profile import StudentProfile
            from app.models.class_student import ClassStudent

            # 查找当前用户对应的ClassStudent记录
            student_class_result = await db.execute(
                select(ClassStudent).join(
                    StudentProfile, StudentProfile.id == ClassStudent.student_profile_id
                ).where(
                    StudentProfile.user_id == teacher_id
                )
            )
            student_class = student_class_result.scalar_one_or_none()

            # 添加调试日志
            if student_class:
                logger.info(f"[DEBUG] Found ClassStudent: id={student_class.id}, student_profile_id={student_class.student_profile_id}")
            else:
                logger.info("[DEBUG] No ClassStudent found for user")

            # 检查用户是否是班级助理
            from app.services.class_assistant_service import ClassAssistantService
            # 获取用户作为班级助理被授权的班级
            assistant_classes = await ClassAssistantService.get_user_assistant_classes(db, teacher_id)
            assistant_class_ids = [cls.id for cls in assistant_classes]
            is_assistant = len(assistant_class_ids) > 0

            # 获取班级列表
            logger.info(f"[DEBUG] User ID: {teacher_id}, is_assistant: {is_assistant}, only_own_records: {only_own_records}, assistant_class_ids: {assistant_class_ids}, student_class: {student_class}")
            logger.info(f"[DEBUG] Filter conditions - class_id: {class_id}, school_name: {school_name}, session: {session}, class_name: {class_name}")

            # 构建查询
            from sqlalchemy.orm import selectinload
            from app.models.user import User

            # 基础查询
            query = select(Growth).options(
                selectinload(Growth.class_info),
                selectinload(Growth.class_student),
                selectinload(Growth.operator)
            )

            # 强制助理身份模式：只显示自己操作的记录
            if force_assistant:
                logger.info(f"[DEBUG] Force assistant mode: User {teacher_id} can see only records they operated")
                # 只显示自己操作的记录
                query = query.where(Growth.operator_id == teacher_id)
                # 如果有授权班级，过滤出自己被授权的班级的记录
                if assistant_class_ids:
                    query = query.where(Growth.class_id.in_(assistant_class_ids))
                else:
                    logger.info("[DEBUG] No authorized classes found for assistant")
                    return [], 0
            # 强制学员身份模式：只显示自己被加减的成长值
            elif force_student and student_class:
                logger.info(f"[DEBUG] Force student mode: User {teacher_id} can see only records related to themselves")
                # 只显示自己被加减的成长值
                query = query.where(Growth.class_student_id == student_class.id)
            # 如果用户既是班级助理又是学员，需要同时显示两种记录
            elif is_assistant and student_class and only_own_records:
                # 双重身份用户，显示自己操作的记录和自己被加减的成长值
                logger.info(f"[DEBUG] User {teacher_id} is both assistant and student, showing both types of records")
                from sqlalchemy import or_
                # 过滤出自己操作的记录或者自己被加减的成长值
                query = query.where(
                    or_(
                        Growth.operator_id == teacher_id,
                        Growth.class_student_id == student_class.id
                    )
                )
                # 如果是助理，还需要过滤出自己被授权的班级的记录
                if assistant_class_ids:
                    query = query.where(Growth.class_id.in_(assistant_class_ids))
            # 优先检查是否是班级助理（但不是学员）
            elif is_assistant:
                # 班级助理只能查看自己操作的本班的成长记录
                logger.info(f"[DEBUG] Class assistant {teacher_id} can see only records they operated in their authorized classes")
                # 首先过滤出自己操作的记录
                query = query.where(Growth.operator_id == teacher_id)
                # 然后过滤出自己被授权的班级的记录
                if assistant_class_ids:
                    query = query.where(Growth.class_id.in_(assistant_class_ids))
                else:
                    logger.info("[DEBUG] No authorized classes found for assistant")
                    return [], 0
            # 对于学员，直接根据class_student_id过滤，不依赖班级列表
            elif only_own_records and student_class:
                # 如果是学员，只显示与自己相关的记录
                logger.info(f"[DEBUG] Filtering growth logs for ClassStudent ID: {student_class.id}")
                query = query.where(Growth.class_student_id == student_class.id)
            else:
                # 对于导师，需要根据班级列表过滤
                # 导师可以查看自己的所有班级
                class_query = select(ClassInfo.id).where(ClassInfo.teacher_id == teacher_id)
                if class_id:
                    class_query = class_query.where(ClassInfo.id == class_id)
                if school_name:
                    class_query = class_query.where(ClassInfo.school_name == school_name)
                if session:
                    class_query = class_query.where(ClassInfo.session == session)
                if class_name:
                    class_query = class_query.where(ClassInfo.class_name == class_name)

                classes = await db.execute(class_query)
                class_ids = [c[0] for c in classes.all()]

                # 如果没有找到班级，尝试获取所有班级（用于测试）
                if not class_ids:
                    all_classes = await db.execute(select(ClassInfo.id))
                    class_ids = [c[0] for c in all_classes.all()]
                    logger.info(f"[DEBUG] Using all class IDs: {class_ids}")

                if not class_ids:
                    logger.info("[DEBUG] No classes found")
                    return [], 0

                # 添加班级过滤
                query = query.where(Growth.class_id.in_(class_ids))

                # 如果指定了只查看自己的记录
                if only_own_records:
                    query = query.where(Growth.operator_id == teacher_id)

            # 时间过滤
            if start_time:
                query = query.where(Growth.created_at >= start_time)
            if end_time:
                query = query.where(Growth.created_at <= end_time)

            # 变动类型过滤
            if change_type == 'positive':
                query = query.where(Growth.change_value > 0)
            elif change_type == 'negative':
                query = query.where(Growth.change_value < 0)

            # 学员姓名过滤
            if student_name:
                # 搜索name_in_class（通过class_student）
                query = query.where(
                    Growth.class_student.has(ClassStudent.name_in_class.contains(student_name))
                )

            # 排除兑换记录
            query = query.where(~Growth.reason.like('%兑换%'))

            # 计算总数
            total_query = select(func.count()).select_from(query.subquery())
            total_result = await db.execute(total_query)
            total = total_result.scalar() or 0

            # 分页和排序
            # 按创建时间倒序排序，最新的记录在前面
            query = query.order_by(Growth.created_at.desc()).offset(skip).limit(limit)

            # 执行查询
            result = await db.execute(query)
            logs = result.scalars().all()

            # 添加调试日志
            logger.info(f"[DEBUG] Growth logs query returned {len(logs)} records")

            # 构建结果
            log_list = []
            for log in logs:
                # 获取学员姓名
                student_name_val = ""
                if log.class_student:
                    student_name_val = log.class_student.name_in_class

                # 获取班级信息
                class_name_val = ""
                school_name_val = ""
                session_val = ""
                if log.class_info:
                    class_name_val = log.class_info.class_name
                    school_name_val = log.class_info.school_name
                    session_val = log.class_info.session

                # 获取操作人姓名
                operator_name = ""
                if log.operator:
                    operator_name = log.operator.real_name

                # 确定操作类型：通过成长记录录入的记录（无论是正还是负），操作类型都是"添加"，只有通过删除操作添加的记录，操作类型才是"删除"
                action = "删除" if log.reason and log.reason.startswith("删除：") else "添加"

                # 转换datetime为字符串，确保可JSON序列化
                created_at_str = None
                updated_at_str = None
                if log.created_at:
                    if hasattr(log.created_at, 'isoformat'):
                        created_at_str = log.created_at.isoformat()
                    else:
                        created_at_str = str(log.created_at)
                if log.updated_at:
                    if hasattr(log.updated_at, 'isoformat'):
                        updated_at_str = log.updated_at.isoformat()
                    else:
                        updated_at_str = str(log.updated_at)

                log_list.append({
                    "id": log.id,
                    "user_id": log.class_student_id,  # 使用 class_student_id 替代 user_id
                    "class_id": log.class_id,
                    "teacher_id": log.teacher_id,
                    "change_score": log.change_value,
                    "reason": log.reason,
                    "operator_id": log.operator_id,
                    "operator_name": operator_name,
                    "input_type": log.input_type,
                    "created_at": created_at_str,
                    "updated_at": updated_at_str,
                    "student_name": student_name_val,
                    "class_name": class_name_val,
                    "school_name": school_name_val,
                    "session": session_val,
                    "action": action  # 添加操作类型字段
                })

            result = (log_list, total)

            # 缓存结果，有效期2分钟（转换为可序列化格式）
            try:
                await cache.set(cache_key, [log_list, total], expire=120)
                logger.info(f"[DEBUG] Growth logs cache set, time: {time.time() - start_time_:.4f}s")
            except Exception as cache_error:
                logger.warning(f"缓存成长值记录失败: {cache_error}")

            return result
        except Exception as e:
            logger.error(f"获取成长值流水失败: {e}")
            import traceback
            logger.error(f"错误堆栈: {traceback.format_exc()}")
            return [], 0

    @staticmethod
    async def update_growth_log(
        db: AsyncSession,
        log_id: int,
        change_score: int,
        reason: str,
        teacher_id: int
    ) -> Growth:
        """修改成长值记录，同时在成长日志表中创建不可变的变更记录"""
        logger.info(f"开始修改成长值记录: log_id={log_id}, change_score={change_score}, reason={reason}, teacher_id={teacher_id}")
        try:
            # 查找成长值记录，显式加载 class_student 关系
            from sqlalchemy.orm import selectinload
            from sqlalchemy import select
            logger.info(f"执行数据库查询: select Growth where id={log_id}")
            result = await db.execute(
                select(Growth).options(
                    selectinload(Growth.class_student),
                    selectinload(Growth.class_info)
                ).where(Growth.id == log_id)
            )
            growth = result.scalar_one_or_none()

            if not growth:
                logger.error(f"成长值记录不存在: log_id={log_id}")
                raise ValueError("成长值记录不存在")

            logger.info(f"找到成长值记录: ID={log_id}, class_id={growth.class_id}, change_value={growth.change_value}, reason={growth.reason}")

            # 验证权限：确保该记录属于当前老师的班级
            logger.info(f"获取班级信息: class_id={growth.class_id}")
            class_info = await db.get(ClassInfo, growth.class_id)
            if not class_info:
                logger.error(f"班级不存在: class_id={growth.class_id}")
                raise ValueError(f"班级不存在: class_id={growth.class_id}")
            if class_info.teacher_id != teacher_id:
                logger.error(f"无权修改该成长值记录: class_info.teacher_id={class_info.teacher_id}, teacher_id={teacher_id}")
                raise ValueError(f"无权修改该成长值记录: class_info.teacher_id={class_info.teacher_id}, teacher_id={teacher_id}")

            logger.info(f"验证权限通过: class_id={growth.class_id}, teacher_id={teacher_id}")

            # 保存原始值用于日志
            original_score = growth.change_value
            original_reason = growth.reason

            # 获取操作用户信息
            from app.models.user import User
            logger.info(f"获取操作用户信息: user_id={teacher_id}")
            operator = await db.get(User, teacher_id)
            operator_name = operator.real_name if operator else "未知用户"
            operator_username = operator.username if operator else ""

            logger.info(f"获取操作用户信息: operator_id={teacher_id}, operator_name={operator_name}, operator_username={operator_username}")

            # 获取学员信息
            student_name = ""
            if growth.class_student:
                student_name = growth.class_student.name_in_class

            logger.info(f"获取学员信息: student_name={student_name}")

            # 记录系统日志
            from app.models.system_log import SystemLog, LogType, LogLevel
            logger.info("创建系统日志记录")
            system_log = SystemLog(
                user_id=teacher_id,
                username=operator_username,
                real_name=operator_name,
                log_type=LogType.UPDATE,
                log_level=LogLevel.INFO,
                module="成长值管理",
                action="修改成长值记录",
                request_params=f"{{\"log_id\": {log_id}, \"student_name\": \"{student_name}\", \"original_score\": {original_score}, \"new_score\": {change_score}, \"original_reason\": \"{original_reason}\", \"new_reason\": \"{reason}\"}}"
            )
            db.add(system_log)

            logger.info("添加系统日志成功")

            # 计算当前成长值和新的成长值
            from sqlalchemy import func
            logger.info(f"计算当前成长值: class_student_id={growth.class_student_id}, log_id={log_id}")
            result = await db.execute(
                select(func.sum(Growth.change_value))
                .where(Growth.class_student_id == growth.class_student_id)
                .where(Growth.id != log_id)  # 排除当前记录
            )
            current_score = result.scalar() or 0
            old_total_score = current_score + original_score
            new_total_score = current_score + change_score

            # 更新原记录
            growth.change_value = change_score
            growth.reason = reason
            growth.operator_id = teacher_id

            logger.info(f"更新原记录: original_score={original_score}, new_score={change_score}, original_reason={original_reason}, new_reason={reason}")

            # 计算变更值
            change_value = change_score - original_score

            # 创建成长值操作日志记录（不可变）
            from app.models.growth_journal import GrowthOperationLog
            # 获取学员姓名（使用之前已经检查过的值）
            # 获取班级名称
            class_name = growth.class_info.class_name if growth.class_info else "未知班级"
            # 获取导师姓名
            teacher_name = "未知导师"
            if growth.class_info and hasattr(growth.class_info, 'teacher') and growth.class_info.teacher:
                teacher_name = growth.class_info.teacher.real_name
            # 获取操作人姓名（使用之前已经获取过的值）

            logger.info(f"创建成长值操作日志记录: student_name={student_name}, class_name={class_name}, teacher_name={teacher_name}, operator_name={operator_name}, old_value={old_total_score}, new_value={new_total_score}, change_value={change_value}")

            growth_operation_log = GrowthOperationLog(
                student_name=student_name,
                class_name=class_name,
                teacher_name=teacher_name,
                operator_name=operator_name,
                old_value=old_total_score,
                new_value=new_total_score,
                change_value=change_value,
                reason=f"修改记录：从{original_score}变更为{change_score}（{reason}）",
                operation_type="update"
            )
            db.add(growth_operation_log)

            logger.info(f"创建成长值操作日志记录: change_value={change_value}, reason={growth_operation_log.reason}")

            logger.info("提交数据库事务")
            await db.commit()
            await db.refresh(growth)
            logger.info(f"修改成长值记录成功: ID={log_id}, 学员{student_name}, 从{original_score}改为{change_score}, 原因从{original_reason}改为{reason}")

            # 清除相关缓存
            from app.core.cache import cache
            await cache.clear_pattern(f"leaderboard:*:{teacher_id}:*")
            await cache.clear_pattern(f"leaderboard:all:{teacher_id}:*")
            await cache.clear_pattern(f"leaderboard:classes:{teacher_id}")

            return growth
        except Exception as e:
            await db.rollback()
            logger.error(f"修改成长值记录失败: {e}")
            import traceback
            logger.error(f"错误堆栈: {traceback.format_exc()}")
            raise

    @staticmethod
    async def delete_growth_log(
        db: AsyncSession,
        log_id: int,
        teacher_id: int,
        reason: str = ""
    ) -> None:
        """删除成长值记录"""
        # 查找成长值记录
        from sqlalchemy.orm import selectinload
        from sqlalchemy import select
        result = await db.execute(
            select(Growth).options(
                selectinload(Growth.class_student),
                selectinload(Growth.class_info)
            ).where(Growth.id == log_id)
        )
        growth = result.scalar_one_or_none()
        if not growth:
            raise ValueError("成长值记录不存在")

        # 验证权限：确保该记录属于当前老师的班级
        class_info = await db.get(ClassInfo, growth.class_id)
        if not class_info or class_info.teacher_id != teacher_id:
            raise ValueError("无权删除该成长值记录")

        # 保存需要更新的班级学员ID和变动分数
        class_student_id = growth.class_student_id
        change_score = growth.change_value

        # 获取操作用户信息
        from app.models.user import User
        operator = await db.get(User, teacher_id)
        operator_name = operator.real_name if operator else "未知用户"

        # 获取学员信息
        student_name = ""
        if growth.class_student:
            student_name = growth.class_student.name_in_class

        # 计算当前成长值和删除后的成长值
        from sqlalchemy import func
        result = await db.execute(
            select(func.sum(Growth.change_value))
            .where(Growth.class_student_id == class_student_id)
            .where(Growth.id != log_id)  # 排除当前记录
        )
        current_score = result.scalar() or 0
        old_total_score = current_score + change_score
        new_total_score = current_score

        # 创建成长值操作日志记录（不可变）
        from app.models.growth_journal import GrowthOperationLog
        # 获取班级名称
        class_name = growth.class_info.class_name if growth.class_info else "未知班级"
        # 获取导师姓名
        teacher_name = "未知导师"
        if growth.class_info and hasattr(growth.class_info, 'teacher') and growth.class_info.teacher:
            teacher_name = growth.class_info.teacher.real_name

        # 格式化删除原因，添加被删除记录的添加时间
        add_date = growth.created_at.strftime("%Y-%m-%d %H:%M:%S")
        delete_reason = f"删除：{reason}（添加时间：{add_date}）"

        growth_operation_log = GrowthOperationLog(
            student_name=student_name,
            class_name=class_name,
            teacher_name=teacher_name,
            operator_name=operator_name,
            old_value=old_total_score,
            new_value=new_total_score,
            change_value=-change_score,
            reason=delete_reason,
            operation_type="delete"
        )
        db.add(growth_operation_log)

        # 删除成长值记录
        await db.delete(growth)

        # 不再使用GrowthScore表存储成长值总额，直接从Growth表计算
        # 移除更新GrowthScore的逻辑

        # 记录系统日志
        from app.models.system_log import SystemLog, LogType, LogLevel
        system_log = SystemLog(
            user_id=teacher_id,
            username=operator.username if operator else "",
            real_name=operator_name,
            log_type=LogType.DELETE,
            log_level=LogLevel.INFO,
            module="成长值管理",
            action="删除成长值记录",
            request_params=f"{{\"log_id\": {log_id}, \"student_name\": \"{student_name}\", \"change_score\": {change_score}, \"reason\": \"{reason}\"}}"
        )
        db.add(system_log)

        try:
            await db.commit()
            logger.info(f"删除成长值记录: ID={log_id}, 学员{class_student_id}, 变动{change_score}")

            # 清除相关缓存
            from app.core.cache import cache
            await cache.clear_pattern(f"leaderboard:*:{teacher_id}:*")
            await cache.clear_pattern(f"leaderboard:all:{teacher_id}:*")
            await cache.clear_pattern(f"leaderboard:classes:{teacher_id}")
        except Exception as e:
            await db.rollback()
            logger.error(f"删除成长值记录失败: {e}")
            raise

    @staticmethod
    async def get_growth_history(
        db: AsyncSession,
        teacher_id: int,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 20,
        student_name: Optional[str] = None,
        only_own_records: bool = False,
        assistant_class_ids: Optional[List[int]] = None
    ) -> tuple[List[Dict[str, Any]], int]:
        """获取成长值变更流水（所有操作，包括添加和删除）"""
        from app.core.logger import logger
        import time
        start_time_ = time.time()

        try:
            # 构建查询
            from app.models.growth_journal import GrowthOperationLog
            from app.models.class_info import ClassInfo
            from app.services.class_assistant_service import ClassAssistantService

            # 查询成长值操作日志记录
            query = select(GrowthOperationLog)

            # 检查用户是否是班级助理
            assistant_classes = await ClassAssistantService.get_user_assistant_classes(db, teacher_id)
            is_assistant = len(assistant_classes) > 0

            # 对于班级助理，显示所有助理操作的日志
            if is_assistant:
                # 获取所有班级助理的姓名
                from app.models.class_assistant import ClassAssistant
                from app.models.user import User
                assistant_query = select(ClassAssistant.assistant_id).distinct()
                assistant_result = await db.execute(assistant_query)
                assistant_ids = [a[0] for a in assistant_result.all()]
                
                # 获取所有助理的姓名
                assistant_names = []
                for aid in assistant_ids:
                    user = await db.get(User, aid)
                    if user:
                        assistant_names.append(user.real_name)
                
                logger.info(f"[DEBUG] Class assistant {teacher_id} can see all logs operated by assistants: {assistant_names}")
                query = query.where(GrowthOperationLog.operator_name.in_(assistant_names))
            elif assistant_class_ids:
                # 如果是班级助理且指定了班级ID列表，只查看这些班级的日志
                # 获取班级名称列表
                class_query = select(ClassInfo.class_name).where(ClassInfo.id.in_(assistant_class_ids))
                class_result = await db.execute(class_query)
                class_names = [c[0] for c in class_result.all()]
                if class_names:
                    query = query.where(GrowthOperationLog.class_name.in_(class_names))

            # 对于其他用户，如果指定了只查看自己的记录
            if only_own_records and not is_assistant:
                # 获取操作人姓名
                from app.models.user import User
                operator = await db.get(User, teacher_id)
                operator_name = operator.real_name if operator else "未知用户"
                query = query.where(GrowthOperationLog.operator_name == operator_name)

            # 时间过滤
            if start_time:
                query = query.where(GrowthOperationLog.created_at >= start_time)
            if end_time:
                query = query.where(GrowthOperationLog.created_at <= end_time)

            # 学员姓名过滤
            if student_name:
                query = query.where(
                    GrowthOperationLog.student_name.contains(student_name)
                )

            # 计算总数
            total_query = select(func.count()).select_from(query.subquery())
            total_result = await db.execute(total_query)
            total = total_result.scalar() or 0

            # 分页
            query = query.offset(skip).limit(limit).order_by(GrowthOperationLog.created_at.desc())

            # 执行查询
            result = await db.execute(query)
            logs = result.scalars().all()

            # 添加调试日志
            logger.info(f"[DEBUG] Growth history query returned {len(logs)} records")
            logger.info(f"[DEBUG] Total records: {total}")

            # 构建结果
            history_list = []
            for log in logs:
                # 构建记录
                history_list.append({
                    "id": log.id,
                    "operator": log.operator_name,
                    "action": log.operation_type,
                    "student_name": log.student_name,
                    "change_score": log.change_value,
                    "reason": log.reason,
                    "created_at": log.created_at,
                    "old_value": log.old_value,
                    "new_value": log.new_value
                })

            result = (history_list, total)

            return result
        except Exception as e:
            import logging
            import traceback
            logging.error(f"获取成长值变更流水失败: {e}")
            logging.error(f"错误堆栈: {traceback.format_exc()}")
            return [], 0

    @staticmethod
    async def get_class_leaderboard(db: AsyncSession, teacher_id: int) -> List[dict]:
        """获取班级排行榜（按成长值排序）"""
        from app.core.logger import logger
        import time
        start_time = time.time()

        try:
            # 尝试从缓存获取
            from app.core.cache import cache
            cache_key = f"class_leaderboard:{teacher_id}"
            cached_result = await cache.get(cache_key)
            if cached_result:
                logger.info(f"[DEBUG] Class leaderboard cache hit, time: {time.time() - start_time:.4f}s")
                return cached_result

            # 获取导师的所有班级
            class_query = select(ClassInfo).where(ClassInfo.teacher_id == teacher_id)
            classes = await db.execute(class_query)
            class_list = classes.scalars().all()

            if not class_list:
                return []

            # 构建班级排行榜数据
            class_leaderboard = []

            # 批量获取所有班级的活跃学员
            from app.models.class_student import BindStatus
            class_ids = [class_info.id for class_info in class_list]

            # 批量获取所有活跃学员
            active_students_query = select(ClassStudent.id, ClassStudent.class_id).where(
                ClassStudent.class_id.in_(class_ids),
                ClassStudent.bind_status == BindStatus.APPROVED,
                ClassStudent.is_deleted == False,
                ClassStudent.is_active == True
            )
            active_students = await db.execute(active_students_query)
            active_student_mapping = {class_id: [] for class_id in class_ids}
            for student_id, class_id in active_students.all():
                active_student_mapping[class_id].append(student_id)

            # 批量获取所有班级的成长值总和
            from sqlalchemy import func
            class_scores_query = select(
                Growth.class_id,
                func.sum(Growth.change_value).label('total_score')
            ).where(
                Growth.class_id.in_(class_ids)
            ).group_by(Growth.class_id)

            class_scores_result = await db.execute(class_scores_query)
            class_scores = {row[0]: int(row[1] or 0) for row in class_scores_result.all()}

            # 构建结果
            for class_info in class_list:
                total_score = class_scores.get(class_info.id, 0)
                class_leaderboard.append({
                    "id": class_info.id,
                    "class_name": class_info.class_name,
                    "school_name": class_info.school_name,
                    "session": class_info.session,
                    "total_score": total_score
                })

            # 按成长值排序
            class_leaderboard.sort(key=lambda x: x['total_score'], reverse=True)

            # 缓存结果，有效期5分钟
            await cache.set(cache_key, class_leaderboard, expire=300)
            logger.info(f"[DEBUG] Class leaderboard cache set, time: {time.time() - start_time:.4f}s")

            return class_leaderboard
        except Exception as e:
            logger.error(f"获取班级排行榜失败: {e}")
            return []

    @staticmethod
    async def batch_import_growth_logs(
        db: AsyncSession,
        records: List[GrowthLogCreate],
        teacher_id: int
    ) -> None:
        """批量导入成长值记录（异步处理）"""
        success_count = 0
        fail_count = 0
        fail_reasons = []

        try:
            for idx, log_data in enumerate(records):
                try:
                    # 查找学员，优先使用学号搜索
                    student = await GrowthService._search_students(db, teacher_id, log_data.student_name, log_data.student_no)
                    if not student:
                        fail_count += 1
                        fail_reasons.append(f"第{idx+1}条记录：学员{log_data.student_name}（学号：{log_data.student_no}）不存在")
                        continue

                    # 检查班级状态
                    class_info = await db.get(ClassInfo, student.class_id)
                    if not class_info or not class_info.status:
                        fail_count += 1
                        fail_reasons.append(f"第{idx+1}条记录：班级不存在或已关闭")
                        continue

                    # 记录成长值变动
                    user_id = None
                    if student.student_profile:
                        user_id = student.student_profile.user_id

                    growth_log = Growth(
                        user_id=user_id,
                        class_student_id=student.id,
                        class_id=student.class_id,
                        teacher_id=teacher_id,
                        change_value=log_data.change_score,
                        reason=log_data.reason,
                        operator_id=teacher_id,
                        input_type=int(log_data.input_type),
                        class_status=class_info.status
                    )

                    db.add(growth_log)
                    success_count += 1

                    # 每100条记录提交一次，避免事务过大
                    if (idx + 1) % 100 == 0:
                        await db.commit()
                        logger.info(f"批量导入成长值：已处理{idx+1}条记录")

                except Exception as e:
                    fail_count += 1
                    fail_reasons.append(f"第{idx+1}条记录：处理失败 - {str(e)}")
                    logger.error(f"批量导入成长值失败：{str(e)}")
                    # 继续处理下一条记录，不中断整个导入过程
                    continue

            # 提交剩余的记录
            await db.commit()

            # 记录批量导入结果
            from app.models.user import User
            from app.models.system_log import SystemLog, LogType, LogLevel

            # 获取操作用户信息
            operator = await db.get(User, teacher_id)
            operator_name = operator.real_name if operator else "未知用户"

            # 记录系统日志
            system_log = SystemLog(
                user_id=teacher_id,
                username=operator.username if operator else "",
                real_name=operator_name,
                log_type=LogType.CREATE,
                log_level=LogLevel.INFO,
                module="成长值管理",
                action="批量导入成长值",
                request_params=f"{{\"total_records\": {len(records)}, \"success_count\": {success_count}, \"fail_count\": {fail_count}}}"
            )
            db.add(system_log)
            await db.commit()

            logger.info(f"批量导入成长值完成：成功{success_count}条，失败{fail_count}条")

            # 清除相关缓存
            from app.core.cache import cache
            await cache.clear_pattern(f"leaderboard:*:{teacher_id}:*")
            await cache.clear_pattern(f"leaderboard:all:{teacher_id}:*")
            await cache.clear_pattern(f"leaderboard:classes:{teacher_id}")

        except Exception as e:
            await db.rollback()
            logger.error(f"批量导入成长值任务失败：{str(e)}")
            # 记录失败日志
            from app.models.user import User
            from app.models.system_log import SystemLog, LogType, LogLevel

            try:
                operator = await db.get(User, teacher_id)
                operator_name = operator.real_name if operator else "未知用户"

                system_log = SystemLog(
                    user_id=teacher_id,
                    username=operator.username if operator else "",
                    real_name=operator_name,
                    log_type=LogType.ERROR,
                    log_level=LogLevel.ERROR,
                    module="成长值管理",
                    action="批量导入成长值",
                    request_params=f"{{\"total_records\": {len(records)}}}",
                    error_message=str(e)
                )
                db.add(system_log)
                await db.commit()
            except:
                pass