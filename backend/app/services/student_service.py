from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, delete
from app.models.class_student import ClassStudent, BindStatus
from app.models.class_info import ClassInfo
from app.models.growth_log import Growth
from app.models.student_note import StudentNote
from app.models.student_tag import StudentTag
from app.models.tag import Tag
from app.core.logger import logger
from app.core.cache import cache, cache_result
from datetime import datetime


class StudentService:
    @staticmethod
    async def get_teacher_students(
        db: AsyncSession,
        teacher_id: int,
        class_id: Optional[int] = None,
        keyword: Optional[str] = None,
        status: Optional[str] = None,
        sort: Optional[str] = None,
        order: Optional[str] = 'asc',
        school_name: Optional[str] = None,
        session: Optional[str] = None,
        is_super_admin: bool = False,
        skip: int = 0,
        limit: int = 20
    ) -> Dict[str, Any]:
        """获取导师的学员列表"""
        import time
        start_time = time.time()
        
        try:
            # 尝试从缓存获取
            cache_key = f"students:teacher:{teacher_id}:class:{class_id or 'all'}:keyword:{keyword or 'none'}:status:{status or 'all'}:sort:{sort or 'none'}:order:{order}:school:{school_name or 'none'}:session:{session or 'all'}:skip:{skip}:limit:{limit}"
            cached_result = await cache.get(cache_key)
            if cached_result:
                logger.info(f"[DEBUG] Student list cache hit, time: {time.time() - start_time:.4f}s")
                return cached_result
            
            logger.info(f"[DEBUG] get_teacher_students called with teacher_id: {teacher_id}, class_id: {class_id}, keyword: {keyword}, status: {status}, sort: {sort}, order: {order}, school_name: {school_name}, session: {session}, is_super_admin: {is_super_admin}, skip: {skip}, limit: {limit}")
            
            # 获取导师的班级
            if is_super_admin:
                # 超级管理员可以访问所有班级
                class_query = select(ClassInfo.id)
            else:
                # 普通老师只能访问自己创建的班级
                class_query = select(ClassInfo.id).where(ClassInfo.teacher_id == teacher_id)
            
            if school_name:
                class_query = class_query.where(ClassInfo.school_name == school_name)
            if class_id:
                class_query = class_query.where(ClassInfo.id == class_id)
            if session:
                class_query = class_query.where(ClassInfo.session == session)
            
            classes = await db.execute(class_query)
            class_ids = [c[0] for c in classes.all()]
            logger.info(f"[DEBUG] Found classes: {class_ids}")
            
            if not class_ids:
                logger.info("[DEBUG] No classes found")
                return {"items": [], "total": 0}
            
            # 获取班级学员，预加载 class_info 和 student_profile 关系，过滤已删除学员
            from sqlalchemy.orm import selectinload
            from app.models.student_profile import StudentProfile
            query = select(ClassStudent).options(
                selectinload(ClassStudent.class_info),
                selectinload(ClassStudent.student_profile)
            ).where(
                ClassStudent.class_id.in_(class_ids),
                ClassStudent.is_deleted == False
            )
            
            # 状态过滤
            if status:
                if status == 'approved':
                    query = query.where(ClassStudent.bind_status == BindStatus.APPROVED)
                elif status == 'pending':
                    query = query.where(ClassStudent.bind_status == BindStatus.PENDING)
                elif status == 'rejected':
                    query = query.where(ClassStudent.bind_status == BindStatus.REJECTED)
                elif status == 'unbound':
                    query = query.where(ClassStudent.bind_status == BindStatus.UNBOUND)
                elif status == 'stopped':
                    query = query.where(ClassStudent.is_active == False)
                elif status == 'active':
                    query = query.where(ClassStudent.is_active == True)
            else:
                # 默认显示正常（活跃）学员
                query = query.where(ClassStudent.is_active == True)
            
            # 关键词搜索
            if keyword:
                query = query.where(
                    or_(
                        ClassStudent.name_in_class.like(f"%{keyword}%"),
                        ClassStudent.student_no_in_class.like(f"%{keyword}%"),
                        ClassStudent.student_profile.has(StudentProfile.real_name.like(f"%{keyword}%"))
                    )
                )
            
            # 执行查询
            result = await db.execute(query)
            bindings = result.scalars().all()
            logger.info(f"[DEBUG] Found {len(bindings)} student bindings")
            
            # 批量获取成长值
            student_ids = [binding.id for binding in bindings]
            growth_scores = await StudentService._get_batch_growth_scores(db, student_ids)
            
            # 批量获取标签
            student_tags = await StudentService._get_batch_student_tags(db, student_ids)
            
            # 构建学员信息
            students = []
            for binding in bindings:
                logger.info(f"[DEBUG] Processing binding: id={binding.id}, class_id={binding.class_id}, name_in_class={binding.name_in_class}, student_no_in_class={binding.student_no_in_class}, student_profile_id={binding.student_profile_id}, bind_status={binding.bind_status}, is_active={binding.is_active}")
                
                # 从批量结果中获取成长值
                scores = growth_scores.get(binding.id, {'available_score': 0, 'total_score': 0})
                available_score = scores['available_score']
                total_score = scores['total_score']
                
                # 从批量结果中获取标签
                tags = student_tags.get(binding.id, [])
                
                # 确保class_info已加载
                class_info = binding.class_info
                logger.info(f"[DEBUG] Class info: id={class_info.id if class_info else None}, class_name={class_info.class_name if class_info else None}, school_name={class_info.school_name if class_info else None}, session={class_info.session if class_info else None}")
                
                # 判断学员是否注册系统
                is_registered = False
                bind_status_text = ""

                if binding.student_profile:
                    if binding.student_profile.user_id is not None:
                        # 有user_id → 学员已自主注册系统
                        is_registered = True
                        # 结合bind_status判断绑定状态
                        if binding.bind_status == BindStatus.NONE:
                            bind_status_text = "未绑定"
                        elif binding.bind_status == BindStatus.PENDING:
                            bind_status_text = "待审核"
                        elif binding.bind_status == BindStatus.APPROVED:
                            bind_status_text = "已绑定"
                        elif binding.bind_status == BindStatus.REJECTED:
                            bind_status_text = "已拒绝"
                        elif binding.bind_status == BindStatus.UNBOUND:
                            bind_status_text = "已解绑"
                        else:
                            bind_status_text = "未知"
                    else:
                        # 无user_id → 学员是导师导入（未注册系统）
                        is_registered = False
                        bind_status_text = "未绑定"
                else:
                    # 无student_profile → 学员是导师导入（未注册系统）
                    is_registered = False
                    bind_status_text = "未绑定"

                # 结合is_active判断是否停用
                if binding.is_active == False:
                    bind_status_text += "（已停用）"
                
                student_info = {
                    "id": binding.id,
                    "name_in_class": binding.name_in_class,
                    "student_no_in_class": binding.student_no_in_class if binding.student_no_in_class else "",
                    "class_id": binding.class_id,
                    "class_name": class_info.class_name if class_info else "未知班级",
                    "class_status": class_info.status if class_info else False,  # 班级状态
                    "school_name": class_info.school_name if class_info else "未知学校",
                    "session": class_info.session if class_info else "",
                    "available_score": available_score,
                    "total_score": total_score,
                    "bind_status": binding.bind_status.value if hasattr(binding.bind_status, 'value') else binding.bind_status,  # 绑定状态值
                    "bind_status_text": bind_status_text,  # 绑定状态文本
                    "is_active": binding.is_active,  # 是否启用
                    "is_registered": is_registered,  # 是否注册系统
                    "tags": tags  # 学员标签
                }
                students.append(student_info)
            
            # 计算总数
            count_query = select(func.count(ClassStudent.id)).where(
                ClassStudent.class_id.in_(class_ids),
                ClassStudent.is_deleted == False
            )
            
            if status:
                if status == 'approved':
                    count_query = count_query.where(ClassStudent.bind_status == BindStatus.APPROVED)
                elif status == 'pending':
                    count_query = count_query.where(ClassStudent.bind_status == BindStatus.PENDING)
                elif status == 'rejected':
                    count_query = count_query.where(ClassStudent.bind_status == BindStatus.REJECTED)
                elif status == 'unbound':
                    count_query = count_query.where(ClassStudent.bind_status == BindStatus.UNBOUND)
                elif status == 'stopped':
                    count_query = count_query.where(ClassStudent.is_active == False)
                elif status == 'active':
                    count_query = count_query.where(ClassStudent.is_active == True)
            else:
                # 默认显示正常（活跃）学员
                count_query = count_query.where(ClassStudent.is_active == True)
            
            if keyword:
                count_query = count_query.where(
                    or_(
                        ClassStudent.name_in_class.like(f"%{keyword}%"),
                        ClassStudent.student_no_in_class.like(f"%{keyword}%"),
                        ClassStudent.student_profile.has(StudentProfile.real_name.like(f"%{keyword}%"))
                    )
                )
            
            count_result = await db.execute(count_query)
            total = count_result.scalar() or 0
            logger.info(f"[DEBUG] Total students: {total}")
            
            # 排序
            if sort:
                if sort == 'name':
                    students.sort(key=lambda x: x['name_in_class'], reverse=(order == 'desc'))
                elif sort == 'class_name':
                    students.sort(key=lambda x: x['class_name'], reverse=(order == 'desc'))
                elif sort == 'available_score':
                    students.sort(key=lambda x: x['available_score'], reverse=(order == 'desc'))
                elif sort == 'bind_status':
                    status_order = {'none': 0, 'pending': 1, 'approved': 2, 'rejected': 3, 'unbound': 4}
                    students.sort(key=lambda x: status_order.get(x['bind_status'], 999), reverse=(order == 'desc'))
            else:
                # 默认排序
                students.sort(key=lambda x: (x['class_name'], x['name_in_class']))
            
            # 分页
            paginated_students = students[skip:skip + limit]
            logger.info(f"[DEBUG] Paginated students: {len(paginated_students)}")
            logger.info(f"[DEBUG] First 5 students: {paginated_students[:5]}")
            
            result = {"items": paginated_students, "total": total}
            
            # 缓存结果，有效期5分钟
            await cache.set(cache_key, result, expire=300)
            logger.info(f"[DEBUG] Student list cache set, time: {time.time() - start_time:.4f}s")
            
            return result
        except Exception as e:
            logger.error(f"获取学员列表失败: {e}")
            import traceback
            traceback.print_exc()
            return {"items": [], "total": 0}
    
    @staticmethod
    async def _get_batch_growth_scores(db: AsyncSession, student_ids: List[int]) -> Dict[int, Dict[str, int]]:
        """批量获取学员成长值"""
        # 计算可用成长值（包括所有成长记录的增减）
        available_score_query = select(
            Growth.class_student_id,
            func.sum(Growth.change_value).label('available_score')
        ).where(
            Growth.class_student_id.in_(student_ids)
        ).group_by(Growth.class_student_id)
        
        # 计算总成长值（只包括通过成长管理增减的记录）
        total_score_query = select(
            Growth.class_student_id,
            func.sum(Growth.change_value).label('total_score')
        ).where(
            Growth.class_student_id.in_(student_ids),
            Growth.input_type.in_([1, 2, 3])  # 1-手动录入，2-语音录入，3-批量导入
        ).group_by(Growth.class_student_id)
        
        # 执行查询
        available_score_result = await db.execute(available_score_query)
        total_score_result = await db.execute(total_score_query)
        
        # 构建结果字典
        available_scores = {row[0]: int(row[1] or 0) for row in available_score_result.all()}
        total_scores = {row[0]: int(row[1] or 0) for row in total_score_result.all()}
        
        # 合并结果
        result = {}
        for student_id in student_ids:
            result[student_id] = {
                'available_score': available_scores.get(student_id, 0),
                'total_score': total_scores.get(student_id, 0)
            }
        
        return result
    
    @staticmethod
    async def _get_batch_student_tags(db: AsyncSession, student_ids: List[int]) -> Dict[int, List[Dict[str, Any]]]:
        """批量获取学员标签"""
        query = select(Tag, StudentTag.class_student_id).join(
            StudentTag, Tag.id == StudentTag.tag_id
        ).where(
            StudentTag.class_student_id.in_(student_ids)
        )
        
        result = await db.execute(query)
        tags_data = result.all()
        
        # 构建结果字典
        tags_map = {student_id: [] for student_id in student_ids}
        for tag, student_id in tags_data:
            tags_map[student_id].append({
                "id": tag.id,
                "name": tag.name,
                "type": tag.type,
                "description": tag.description
            })
        
        return tags_map
    
    @staticmethod
    async def _get_batch_operator_info(db: AsyncSession, student_ids: List[int]) -> Dict[int, str]:
        """批量获取学员操作人信息"""
        from app.models.student_operation_log import StudentOperationLog
        from sqlalchemy import func
        
        # 为每个学员获取最近的操作日志
        query = select(
            StudentOperationLog.class_student_id,
            StudentOperationLog.operator_name
        ).where(
            StudentOperationLog.class_student_id.in_(student_ids),
            StudentOperationLog.operation_type.in_("stop", "unbind")
        ).order_by(
            StudentOperationLog.class_student_id,
            StudentOperationLog.created_at.desc()
        )
        
        result = await db.execute(query)
        logs = result.all()
        
        # 构建结果字典，只保留每个学员的最新操作记录
        operator_map = {}
        for student_id, operator_name in logs:
            if student_id not in operator_map:
                operator_map[student_id] = operator_name
        
        return operator_map
    
    @staticmethod
    async def get_student_tags(db: AsyncSession, class_student_id: int) -> List[Dict[str, Any]]:
        """获取学员标签"""
        try:
            query = select(Tag).join(StudentTag).where(StudentTag.class_student_id == class_student_id)
            result = await db.execute(query)
            tags = result.scalars().all()
            return [{
                "id": tag.id,
                "name": tag.name,
                "type": tag.type,
                "description": tag.description
            } for tag in tags]
        except Exception as e:
            logger.error(f"获取学员标签失败: {e}")
            return []
    
    @staticmethod
    async def update_student_tags(db: AsyncSession, class_student_id: int, tag_ids: List[int]) -> None:
        """更新学员标签"""
        try:
            # 先删除现有标签
            delete_query = delete(StudentTag).where(StudentTag.class_student_id == class_student_id)
            await db.execute(delete_query)
            
            # 确保标签ID唯一
            unique_tag_ids = list(set(tag_ids))
            
            # 添加新标签
            for tag_id in unique_tag_ids:
                student_tag = StudentTag(
                    class_student_id=class_student_id,
                    tag_id=tag_id
                )
                db.add(student_tag)
            
            # 注意：这里不提交事务，由调用方负责提交
        except Exception as e:
            logger.error(f"更新学员标签失败: {e}")
            raise
    
    @staticmethod
    async def get_history_students(
        db: AsyncSession,
        teacher_id: int,
        class_id: Optional[int] = None,
        keyword: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
        is_super_admin: bool = False
    ) -> tuple[List[Dict[str, Any]], int]:
        """获取历史学员（已删除的学员）"""
        import time
        start_time = time.time()
        
        try:
            # 尝试从缓存获取
            cache_key = f"students:history:teacher:{teacher_id}:class:{class_id or 'all'}:keyword:{keyword or 'none'}:skip:{skip}:limit:{limit}"
            cached_result = await cache.get(cache_key)
            if cached_result:
                logger.info(f"[DEBUG] History student list cache hit, time: {time.time() - start_time:.4f}s")
                return cached_result
            
            logger.info(f"[DEBUG] get_history_students called with teacher_id: {teacher_id}, class_id: {class_id}, keyword: {keyword}, skip: {skip}, limit: {limit}, is_super_admin: {is_super_admin}")
            
            # 获取导师的班级
            if is_super_admin:
                # 超级管理员可以访问所有班级
                class_query = select(ClassInfo.id)
            else:
                # 普通老师只能访问自己创建的班级
                class_query = select(ClassInfo.id).where(ClassInfo.teacher_id == teacher_id)
            
            if class_id:
                class_query = class_query.where(ClassInfo.id == class_id)
            
            classes = await db.execute(class_query)
            class_ids = [c[0] for c in classes.all()]
            logger.info(f"[DEBUG] Found classes: {class_ids}")
            
            if not class_ids:
                logger.info("[DEBUG] No classes found")
                return [], 0
            
            # 构建基础查询，查询当前导师班级中已删除的学员
            from sqlalchemy.orm import selectinload
            from app.models.student_profile import StudentProfile
            base_query = select(ClassStudent).options(
                selectinload(ClassStudent.class_info),
                selectinload(ClassStudent.student_profile)
            ).where(
                ClassStudent.class_id.in_(class_ids),
                ClassStudent.is_deleted == True
            )
            
            # 关键词搜索
            if keyword:
                base_query = base_query.where(
                    or_(
                        ClassStudent.name_in_class.like(f"%{keyword}%"),
                        ClassStudent.student_no_in_class.like(f"%{keyword}%")
                    )
                )
            
            # 计算总数
            count_query = select(func.count(ClassStudent.id)).where(
                ClassStudent.class_id.in_(class_ids),
                ClassStudent.is_deleted == True
            )
            if keyword:
                count_query = count_query.where(
                    or_(
                        ClassStudent.name_in_class.like(f"%{keyword}%"),
                        ClassStudent.student_no_in_class.like(f"%{keyword}%")
                    )
                )
            
            count_result = await db.execute(count_query)
            total = count_result.scalar() or 0
            logger.info(f"[DEBUG] Total history students: {total}")
            
            # 添加排序和分页
            query = base_query.order_by(ClassStudent.deleted_at.desc()).offset(skip).limit(limit)
            
            # 执行查询
            result = await db.execute(query)
            bindings = result.scalars().all()
            logger.info(f"[DEBUG] Found {len(bindings)} history student bindings")
            
            # 构建学员信息
            students = []
            for binding in bindings:
                logger.info(f"[DEBUG] Processing binding: id={binding.id}, class_id={binding.class_id}, name_in_class={binding.name_in_class}, student_no_in_class={binding.student_no_in_class}, student_profile_id={binding.student_profile_id}, bind_status={binding.bind_status}")
                
                # 获取成长值 - 统一从Growth表计算
                growth_query = select(func.sum(Growth.change_value)).where(
                    Growth.class_student_id == binding.id
                )
                growth_result = await db.execute(growth_query)
                growth_score = growth_result.scalar() or 0
                # 转换为整数类型，避免Decimal序列化错误
                growth_score = int(growth_score)
                logger.info(f"[DEBUG] Student growth_score={growth_score}")
                
                # 获取学员标签
                tags = await StudentService.get_student_tags(db, binding.id)
                logger.info(f"[DEBUG] Student {binding.name_in_class} tags: {tags}")
                
                # 确保class_info已加载
                class_info = binding.class_info
                logger.info(f"[DEBUG] Class info: id={class_info.id if class_info else None}, class_name={class_info.class_name if class_info else None}, school_name={class_info.school_name if class_info else None}, session={class_info.session if class_info else None}")
                
                # 判断学员是否注册系统
                is_registered = False
                bind_status_text = "已删除"
                
                if binding.student_profile:
                    if binding.student_profile.user_id is not None:
                        # 有user_id → 学员已自主注册系统
                        is_registered = True
                    else:
                        # 无user_id → 学员是导师导入（未注册系统）
                        is_registered = False
                else:
                    # 无student_profile → 学员是导师导入（未注册系统）
                    is_registered = False
                
                # 获取操作人信息（从学员操作日志中查找）
                from app.models.student_operation_log import StudentOperationLog
                operation_log_query = select(StudentOperationLog).where(
                    StudentOperationLog.class_student_id == binding.id,
                    StudentOperationLog.operation_type.in_(["stop", "unbind"])
                ).order_by(StudentOperationLog.created_at.desc()).limit(1)
                operation_log_result = await db.execute(operation_log_query)
                operation_log = operation_log_result.scalar_one_or_none()
                operator_name = operation_log.operator_name if operation_log else "未知"
                
                student_info = {
                    "id": binding.id,
                    "name_in_class": binding.name_in_class,
                    "student_no_in_class": binding.student_no_in_class if binding.student_no_in_class else "",
                    "class_id": binding.class_id,
                    "class_name": class_info.class_name if class_info else "未知班级",
                    "school_name": class_info.school_name if class_info else "未知学校",
                    "session": class_info.session if class_info else "",
                    "available_score": growth_score,
                    "is_approved": binding.bind_status == BindStatus.APPROVED,  # 转换为布尔值
                    "is_registered": is_registered,  # 是否注册系统
                    "bind_status_text": bind_status_text,  # 绑定状态文本
                    "tags": tags,  # 学员标签
                    "deleted_at": binding.deleted_at,
                    "remove_reason": binding.remove_reason,
                    "operator_name": operator_name  # 操作人
                }
                students.append(student_info)
            
            logger.info(f"[DEBUG] Final history student list length: {len(students)}")
            
            result = (students, total)
            
            # 缓存结果，有效期5分钟
            await cache.set(cache_key, result, expire=300)
            logger.info(f"[DEBUG] History student list cache set, time: {time.time() - start_time:.4f}s")
            
            return result
        except Exception as e:
            logger.error(f"获取历史学员列表失败: {e}")
            return [], 0
    
    @staticmethod
    async def get_student_note(db: AsyncSession, class_student_id: int) -> Optional[StudentNote]:
        """获取学员备注"""
        from sqlalchemy import select
        query = select(StudentNote).where(StudentNote.class_student_id == class_student_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_or_update_student_note(db: AsyncSession, class_student_id: int, learning_characteristics: str, personality_suggestions: str, performance_summary: str, real_name: str = None, tags: str = None) -> StudentNote:
        """创建或更新学员备注"""
        from sqlalchemy import select
        query = select(StudentNote).where(StudentNote.class_student_id == class_student_id)
        result = await db.execute(query)
        note = result.scalar_one_or_none()

        if note:
            note.learning_characteristics = learning_characteristics
            note.personality_suggestions = personality_suggestions
            note.performance_summary = performance_summary
            if real_name is not None:
                note.real_name = real_name
            if tags is not None:
                note.tags = tags
        else:
            note = StudentNote(
                class_student_id=class_student_id,
                real_name=real_name,
                learning_characteristics=learning_characteristics,
                personality_suggestions=personality_suggestions,
                performance_summary=performance_summary,
                tags=tags
            )
            db.add(note)

        return note
    
    @staticmethod
    async def delete_student(db: AsyncSession, student_class_id: int, teacher_id: int, reason: str) -> dict:
        """删除学员"""
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        from datetime import datetime
        
        # 获取学员信息
        query = select(ClassStudent).options(
            selectinload(ClassStudent.class_info),
            selectinload(ClassStudent.student_profile)
        ).where(ClassStudent.id == student_class_id)
        result = await db.execute(query)
        student_class = result.scalar_one_or_none()
        
        if not student_class:
            raise ValueError("学员不存在")
        
        # 检查是否是该班级的导师
        class_info = student_class.class_info
        if not class_info or class_info.teacher_id != teacher_id:
            raise ValueError("无权限操作此学员")
        
        # 检查班级是否已关闭
        if class_info.status != "active":
            raise ValueError("班级已关闭，无法操作学员")
        
        # 保存学员信息，用于后续记录操作日志
        old_student_info = {
            "id": student_class.id,
            "class_id": student_class.class_id,
            "name_in_class": student_class.name_in_class,
            "student_no_in_class": student_class.student_no_in_class,
            "student_profile_id": student_class.student_profile_id,
            "bind_status": student_class.bind_status.value,
            "is_active": student_class.is_active,
            "is_deleted": student_class.is_deleted
        }
        
        # 标记为已删除，保留所有历史数据
        student_class.is_deleted = True
        student_class.deleted_at = datetime.utcnow()
        student_class.remove_reason = reason
        
        # 释放学号占用
        student_class.student_no_in_class = None

        await db.commit()
        await db.refresh(student_class)
        
        # 保存更新后的学员信息
        new_student_info = {
            "id": student_class.id,
            "class_id": student_class.class_id,
            "name_in_class": student_class.name_in_class,
            "student_no_in_class": student_class.student_no_in_class,
            "student_profile_id": student_class.student_profile_id,
            "bind_status": student_class.bind_status.value,
            "is_active": student_class.is_active,
            "is_deleted": student_class.is_deleted
        }
        
        logger.info(f"删除学员: student_class_id={student_class_id}, teacher_id={teacher_id}, reason={reason}")
        return {"status": "deleted", "message": "学员已删除", "old_student_info": old_student_info, "new_student_info": new_student_info, "class_name": class_info.class_name}
    
    @staticmethod
    async def stop_student(db: AsyncSession, student_class_id: int, teacher_id: int, reason: str) -> dict:
        """停用学员（休学）"""
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        from datetime import datetime
        
        # 获取学员信息
        query = select(ClassStudent).options(
            selectinload(ClassStudent.class_info),
            selectinload(ClassStudent.student_profile)
        ).where(ClassStudent.id == student_class_id)
        result = await db.execute(query)
        student_class = result.scalar_one_or_none()
        
        if not student_class:
            raise ValueError("学员不存在")
        
        # 检查是否是该班级的导师
        class_info = student_class.class_info
        if not class_info or class_info.teacher_id != teacher_id:
            raise ValueError("无权限操作此学员")
        
        # 检查班级是否已关闭
        if class_info.status != "active":
            raise ValueError("班级已关闭，无法操作学员")
        
        # 保存学员信息，用于后续记录操作日志
        old_student_info = {
            "id": student_class.id,
            "class_id": student_class.class_id,
            "name_in_class": student_class.name_in_class,
            "student_no_in_class": student_class.student_no_in_class,
            "student_profile_id": student_class.student_profile_id,
            "bind_status": student_class.bind_status.value,
            "is_active": student_class.is_active,
            "is_deleted": student_class.is_deleted
        }
        
        # 标记为停用
        student_class.is_active = False

        await db.commit()
        await db.refresh(student_class)
        
        # 保存更新后的学员信息
        new_student_info = {
            "id": student_class.id,
            "class_id": student_class.class_id,
            "name_in_class": student_class.name_in_class,
            "student_no_in_class": student_class.student_no_in_class,
            "student_profile_id": student_class.student_profile_id,
            "bind_status": student_class.bind_status.value,
            "is_active": student_class.is_active,
            "is_deleted": student_class.is_deleted
        }
        
        logger.info(f"停用学员: student_class_id={student_class_id}, teacher_id={teacher_id}, reason={reason}")
        return {"status": "stopped", "message": "学员已停用", "old_student_info": old_student_info, "new_student_info": new_student_info, "class_name": class_info.class_name}
    
    @staticmethod
    async def activate_student(db: AsyncSession, student_class_id: int, teacher_id: int) -> dict:
        """启用学员（复学）"""
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        
        # 获取学员信息
        query = select(ClassStudent).options(
            selectinload(ClassStudent.class_info),
            selectinload(ClassStudent.student_profile)
        ).where(ClassStudent.id == student_class_id)
        result = await db.execute(query)
        student_class = result.scalar_one_or_none()
        
        if not student_class:
            raise ValueError("学员不存在")
        
        # 检查是否是该班级的导师
        class_info = student_class.class_info
        if not class_info or class_info.teacher_id != teacher_id:
            raise ValueError("无权限操作此学员")
        
        # 检查班级是否已关闭
        if class_info.status != "active":
            raise ValueError("班级已关闭，无法操作学员")
        
        # 保存学员信息，用于后续记录操作日志
        old_student_info = {
            "id": student_class.id,
            "class_id": student_class.class_id,
            "name_in_class": student_class.name_in_class,
            "student_no_in_class": student_class.student_no_in_class,
            "student_profile_id": student_class.student_profile_id,
            "bind_status": student_class.bind_status.value,
            "is_active": student_class.is_active,
            "is_deleted": student_class.is_deleted
        }
        
        # 标记为启用
        student_class.is_active = True

        await db.commit()
        await db.refresh(student_class)
        
        # 保存更新后的学员信息
        new_student_info = {
            "id": student_class.id,
            "class_id": student_class.class_id,
            "name_in_class": student_class.name_in_class,
            "student_no_in_class": student_class.student_no_in_class,
            "student_profile_id": student_class.student_profile_id,
            "bind_status": student_class.bind_status.value,
            "is_active": student_class.is_active,
            "is_deleted": student_class.is_deleted
        }
        
        logger.info(f"启用学员: student_class_id={student_class_id}, teacher_id={teacher_id}")
        return {"status": "activated", "message": "学员已启用", "old_student_info": old_student_info, "new_student_info": new_student_info, "class_name": class_info.class_name}
    
    @staticmethod
    async def unbind_student(db: AsyncSession, student_class_id: int, teacher_id: int, reason: str) -> dict:
        """解除绑定关系"""
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        
        # 获取学员信息
        query = select(ClassStudent).options(
            selectinload(ClassStudent.class_info),
            selectinload(ClassStudent.student_profile)
        ).where(ClassStudent.id == student_class_id)
        result = await db.execute(query)
        student_class = result.scalar_one_or_none()
        
        if not student_class:
            raise ValueError("学员不存在")
        
        # 检查是否是该班级的导师
        class_info = student_class.class_info
        if not class_info or class_info.teacher_id != teacher_id:
            raise ValueError("无权限操作此学员")
        
        # 检查班级是否已关闭
        if class_info.status != "active":
            raise ValueError("班级已关闭，无法操作学员")
        
        # 检查绑定状态是否为已绑定
        if student_class.bind_status != BindStatus.APPROVED:
            raise ValueError("只有已绑定的学员才能解绑")
        
        # 保存学员信息，用于后续记录操作日志
        old_student_info = {
            "id": student_class.id,
            "class_id": student_class.class_id,
            "name_in_class": student_class.name_in_class,
            "student_no_in_class": student_class.student_no_in_class,
            "student_profile_id": student_class.student_profile_id,
            "bind_status": student_class.bind_status.value,
            "is_active": student_class.is_active,
            "is_deleted": student_class.is_deleted
        }
        
        # 标记为已解绑
        student_class.bind_status = BindStatus.UNBOUND

        await db.commit()
        await db.refresh(student_class)
        
        # 保存更新后的学员信息
        new_student_info = {
            "id": student_class.id,
            "class_id": student_class.class_id,
            "name_in_class": student_class.name_in_class,
            "student_no_in_class": student_class.student_no_in_class,
            "student_profile_id": student_class.student_profile_id,
            "bind_status": student_class.bind_status.value,
            "is_active": student_class.is_active,
            "is_deleted": student_class.is_deleted
        }
        
        logger.info(f"解绑学员: student_class_id={student_class_id}, teacher_id={teacher_id}, reason={reason}")
        return {"status": "unbound", "message": "学员已解绑", "old_student_info": old_student_info, "new_student_info": new_student_info, "class_name": class_info.class_name}
    
    @staticmethod
    async def get_student_class_by_id(db: AsyncSession, student_class_id: int) -> Optional[ClassStudent]:
        """根据ID获取班级学员信息"""
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        query = select(ClassStudent).options(
            selectinload(ClassStudent.class_info),
            selectinload(ClassStudent.student_profile)
        ).where(ClassStudent.id == student_class_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_student_info(db: AsyncSession, student_class_id: int, teacher_id: int, real_name: str) -> dict:
        """更新学员基本信息"""
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        
        # 获取学员信息
        query = select(ClassStudent).options(
            selectinload(ClassStudent.class_info),
            selectinload(ClassStudent.student_profile)
        ).where(ClassStudent.id == student_class_id)
        result = await db.execute(query)
        student_class = result.scalar_one_or_none()
        
        if not student_class:
            raise ValueError("学员不存在")
        
        # 检查是否是该班级的导师
        class_info = student_class.class_info
        if not class_info or class_info.teacher_id != teacher_id:
            raise ValueError("无权限操作此学员")
        
        # 检查班级是否已关闭
        if not class_info.status:
            raise ValueError("班级已关闭，无法操作学员")
        
        # 保存原始信息，用于后续记录操作日志
        old_name = student_class.name_in_class
        old_student_info = {
            "id": student_class.id,
            "class_id": student_class.class_id,
            "name_in_class": student_class.name_in_class,
            "student_no_in_class": student_class.student_no_in_class,
            "student_profile_id": student_class.student_profile_id,
            "bind_status": student_class.bind_status.value,
            "is_active": student_class.is_active,
            "is_deleted": student_class.is_deleted
        }
        
        # 只有当姓名实际改变时才执行更新
        if student_class.name_in_class != real_name:
            # 更新学员信息
            student_class.name_in_class = real_name
            
            await db.commit()
            await db.refresh(student_class)
            
            # 保存更新后的学员信息
            new_student_info = {
                "id": student_class.id,
                "class_id": student_class.class_id,
                "name_in_class": student_class.name_in_class,
                "student_no_in_class": student_class.student_no_in_class,
                "student_profile_id": student_class.student_profile_id,
                "bind_status": student_class.bind_status.value,
                "is_active": student_class.is_active,
                "is_deleted": student_class.is_deleted
            }
            
            logger.info(f"更新学员信息: student_class_id={student_class_id}, teacher_id={teacher_id}, old_name={old_name}, new_name={real_name}")
            return {
                "status": "updated", 
                "message": "学员信息已更新", 
                "old_student_info": old_student_info,
                "new_student_info": new_student_info,
                "class_name": class_info.class_name
            }
        else:
            # 姓名没有改变，不执行更新
            logger.info(f"学员姓名未改变，跳过更新: student_class_id={student_class_id}, name={real_name}")
            return {
                "status": "unchanged", 
                "message": "学员信息未变更",
                "class_name": class_info.class_name
            }
    
    @staticmethod
    async def add_student(db: AsyncSession, class_id: int, student_no: str, real_name: str, teacher_id: int) -> dict:
        """添加学员"""
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        
        # 检查班级是否存在，并且是该导师的班级
        class_query = select(ClassInfo).where(ClassInfo.id == class_id, ClassInfo.teacher_id == teacher_id)
        class_result = await db.execute(class_query)
        class_info = class_result.scalar_one_or_none()
        
        if not class_info:
            raise ValueError("班级不存在或无权限操作")
        
        # 检查班级是否已关闭
        if not class_info.status:
            raise ValueError("班级已关闭，无法添加学员")
        
        # 检查学号是否已存在（在该班级内，且未删除）
        existing_student_query = select(ClassStudent).where(
            ClassStudent.class_id == class_id,
            ClassStudent.student_no_in_class == student_no,
            ClassStudent.is_deleted == False
        )
        existing_student_result = await db.execute(existing_student_query)
        existing_student = existing_student_result.scalar_one_or_none()
        
        if existing_student:
            raise ValueError("学号已存在")
        
        # 创建新学员
        new_student = ClassStudent(
            class_id=class_id,
            name_in_class=real_name,
            student_no_in_class=student_no,
            bind_status=BindStatus.NONE,
            is_active=True,
            is_deleted=False
        )
        
        db.add(new_student)
        await db.commit()
        await db.refresh(new_student)
        
        # 构建返回信息
        student_info = {
            "id": new_student.id,
            "class_id": new_student.class_id,
            "name_in_class": new_student.name_in_class,
            "student_no_in_class": new_student.student_no_in_class,
            "bind_status": new_student.bind_status if isinstance(new_student.bind_status, str) else new_student.bind_status.value,
            "is_active": new_student.is_active,
            "is_deleted": new_student.is_deleted
        }
        
        logger.info(f"添加学员: class_id={class_id}, student_no={student_no}, real_name={real_name}, teacher_id={teacher_id}")
        return {
            "status": "added", 
            "message": "学员添加成功", 
            "student_info": student_info,
            "class_name": class_info.class_name
        }