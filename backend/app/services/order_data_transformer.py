from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.class_student import ClassStudent
from app.models.student_profile import StudentProfile
from app.models.user import User
from app.models.gift import Gift
from app.models.class_info import ClassInfo
from app.core.logger import logger


class OrderDataTransformer:
    @staticmethod
    async def get_student_name(
        db: AsyncSession,
        class_student_id: int
    ) -> str:
        try:
            student_result = await db.execute(
                select(ClassStudent).options(
                    selectinload(ClassStudent.student_profile).selectinload(StudentProfile.user)
                ).where(ClassStudent.id == class_student_id)
            )
            student = student_result.scalar_one_or_none()
            
            if not student:
                return ""
            
            if student.student_profile and student.student_profile.user:
                return student.student_profile.user.real_name or ""
            else:
                return student.name_in_class or ""
                
        except Exception as e:
            logger.warning(f"获取学生姓名失败: class_student_id={class_student_id}, error={e}")
            return ""
    
    @staticmethod
    async def get_operator_name(
        db: AsyncSession,
        operator_id: Optional[int],
        class_id: Optional[int] = None
    ) -> str:
        if not operator_id:
            return ""
        
        try:
            if class_id:
                student_result = await db.execute(
                    select(ClassStudent).join(StudentProfile).where(
                        StudentProfile.user_id == operator_id,
                        ClassStudent.class_id == class_id
                    )
                )
                student = student_result.scalar_one_or_none()
                
                if student:
                    return student.name_in_class or ""
            
            operator_result = await db.execute(
                select(User).where(User.id == operator_id)
            )
            operator = operator_result.scalar_one_or_none()
            
            if operator:
                return operator.real_name or operator.username or ""
                
            return ""
            
        except Exception as e:
            logger.warning(f"获取操作人姓名失败: operator_id={operator_id}, error={e}")
            return ""
    
    @staticmethod
    async def get_gift_info(
        db: AsyncSession,
        gift_id: int
    ) -> Optional[Dict[str, Any]]:
        try:
            gift_result = await db.execute(
                select(Gift).where(Gift.id == gift_id)
            )
            gift = gift_result.scalar_one_or_none()
            
            if not gift:
                return None
                
            return {
                "id": gift.id,
                "name": gift.name,
                "price": gift.price,
                "image_url": gift.image_url
            }
            
        except Exception as e:
            logger.warning(f"获取礼品信息失败: gift_id={gift_id}, error={e}")
            return None
    
    @staticmethod
    async def get_class_info(
        db: AsyncSession,
        class_id: int
    ) -> Optional[Dict[str, Any]]:
        try:
            class_result = await db.execute(
                select(ClassInfo).where(ClassInfo.id == class_id)
            )
            class_info = class_result.scalar_one_or_none()
            
            if not class_info:
                return None
                
            return {
                "id": class_info.id,
                "class_name": class_info.class_name,
                "school_name": class_info.school_name
            }
            
        except Exception as e:
            logger.warning(f"获取班级信息失败: class_id={class_id}, error={e}")
            return None
    
    @staticmethod
    async def build_order_response(
        db: AsyncSession,
        order: Any,
        include_operator: bool = True,
        include_qr_code: bool = False,
        order_id_field: str = "id"
    ) -> Dict[str, Any]:
        student_name = await OrderDataTransformer.get_student_name(db, order.class_student_id)
        gift_info = await OrderDataTransformer.get_gift_info(db, order.gift_id)
        class_info = await OrderDataTransformer.get_class_info(db, order.class_id)
        
        response = {
            "id": getattr(order, order_id_field, order.id),
            "student_name": student_name,
            "gift_name": gift_info["name"] if gift_info else "",
            "class_name": class_info["class_name"] if class_info else "",
            "price": order.price,
            "status": order.status,
            "created_at": order.created_at
        }
        
        if include_qr_code and hasattr(order, 'qr_code'):
            response["qr_code"] = order.qr_code
        
        if include_operator and getattr(order, 'operator_id', None):
            operator_name = await OrderDataTransformer.get_operator_name(
                db, order.operator_id, order.class_id
            )
            response["operator_name"] = operator_name
        
        if hasattr(order, 'action'):
            response["action"] = order.action
        
        if hasattr(order, 'remarks'):
            response["remarks"] = order.remarks or ""
        
        if hasattr(order, 'operated_at'):
            response["operated_at"] = order.operated_at
        
        return response