from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.user import User, Role

from app.models.student_profile import StudentProfile
from app.schemas.user import UserCreate, UserUpdate, UserLogin
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.logger import logger


class UserService:
    """用户服务"""
    
    MAX_LOGIN_ERRORS = 5
    LOCK_DURATION_MINUTES = 10
    CAPTCHA_THRESHOLD = 3
    
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_role_by_name(db: AsyncSession, role_name: str) -> Optional[Role]:
        """根据名称获取角色"""
        result = await db.execute(select(Role).where(Role.role_name == role_name))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_role_by_id(db: AsyncSession, role_id: int) -> Optional[Role]:
        """根据ID获取角色"""
        result = await db.execute(select(Role).where(Role.id == role_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate, is_approved: bool = False) -> User:
        """创建用户"""
        # 检查邮箱是否已被注册
        existing_user = await UserService.get_user_by_email(db, user_data.email)
        if existing_user:
            raise ValueError("该邮箱已被注册")
        
        # 检查用户名是否已被注册
        result = await db.execute(select(User).where(User.username == user_data.username))
        if result.scalar_one_or_none():
            raise ValueError("该用户名已被注册")
        
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            password=hashed_password,
            real_name=user_data.real_name,
            role_id=user_data.role_id,
            status=is_approved
        )
        
        db.add(db_user)
        await db.flush()
        
        role = await UserService.get_role_by_id(db, user_data.role_id)
        if role and role.role_name == "student":
            # 创建学员档案
            student_profile = StudentProfile(
                user_id=db_user.id,
                real_name=user_data.real_name
            )
            db.add(student_profile)
        
        await db.commit()
        await db.refresh(db_user)
        
        logger.info(f"用户创建成功: {db_user.email}, 角色: {role.role_name if role else 'unknown'}")
        return db_user
    
    @staticmethod
    async def authenticate_user(
        db: AsyncSession, 
        username: str, 
        password: str,
        captcha: Optional[str] = None,
        captcha_id: Optional[str] = None
    ) -> tuple[Optional[User], Optional[str]]:
        """
        验证用户登录
        返回: (user, error_message)
        """
        from app.services.captcha_service import CaptchaService
        
        # 支持使用邮箱或用户名登录
        result = await db.execute(
            select(User).options(selectinload(User.role)).where(
                or_(User.username == username, User.email == username)
            )
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return None, "用户名或密码错误"
        
        if user.locked_until and datetime.utcnow() < user.locked_until:
            remaining = (user.locked_until - datetime.utcnow()).seconds // 60
            return None, f"账号已锁定，请{remaining}分钟后再试"
        
        if (user.login_error_count or 0) >= UserService.CAPTCHA_THRESHOLD:
            if not captcha or not captcha_id:
                return None, "NEED_CAPTCHA"
            if not CaptchaService.verify_captcha(captcha_id, captcha):
                return None, "验证码错误"
        
        if not verify_password(password, user.password):
            user.login_error_count += 1
            
            if (user.login_error_count or 0) >= UserService.MAX_LOGIN_ERRORS:
                user.locked_until = datetime.now() + timedelta(minutes=UserService.LOCK_DURATION_MINUTES)
                logger.warning(f"账号锁定: {user.email or user.username}")
            
            await db.commit()
            remaining_attempts = UserService.MAX_LOGIN_ERRORS - (user.login_error_count or 0)
            if remaining_attempts > 0:
                return None, f"密码错误，还剩{remaining_attempts}次机会"
            else:
                return None, "密码错误次数过多，账号已锁定10分钟"
        
        user.login_error_count = 0
        user.locked_until = None
        user.last_login_time = datetime.now()
        user.login_count += 1
        
        # 刷新用户对象，确保获取最新的角色信息
        await db.commit()
        await db.refresh(user)
        
        # 重新加载角色信息
        result = await db.execute(
            select(User).options(selectinload(User.role)).where(User.id == user.id)
        )
        user = result.scalar_one_or_none()
        
        return user, None
    
    @staticmethod
    async def update_user(db: AsyncSession, user: User, user_data: UserUpdate) -> User:
        """更新用户信息"""
        if user_data.real_name:
            user.real_name = user_data.real_name
        
        if user_data.phone and user_data.phone != user.phone:
            user.phone = user_data.phone
        
        await db.commit()
        await db.refresh(user)
        
        logger.info(f"用户信息更新: {user.id}")
        return user
    
    @staticmethod
    async def get_users(
        db: AsyncSession,
        role_id: Optional[int] = None,
        status: Optional[bool] = None,
        keyword: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[User], int]:
        """获取用户列表"""
        query = select(User)
        count_query = select(func.count(User.id))
        
        if role_id:
            query = query.where(User.role_id == role_id)
            count_query = count_query.where(User.role_id == role_id)
        
        if status is not None:
            query = query.where(User.status == status)
            count_query = count_query.where(User.status == status)
        
        if keyword:
            keyword_filter = or_(
                User.real_name.contains(keyword),
                User.email.contains(keyword)
            )
            query = query.where(keyword_filter)
            count_query = count_query.where(keyword_filter)
        
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0
        
        query = query.offset(skip).limit(limit).order_by(User.created_at.desc())
        result = await db.execute(query)
        users = result.scalars().all()
        
        return users, total
    
    @staticmethod
    async def approve_user(db: AsyncSession, user_id: int) -> User:
        """审核通过用户（导师注册）"""
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            raise ValueError("用户不存在")
        
        user.status = True
        await db.commit()
        await db.refresh(user)
        
        logger.info(f"用户审核通过: {user.id}")
        return user
    
    @staticmethod
    async def disable_user(db: AsyncSession, user_id: int) -> User:
        """禁用用户"""
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            raise ValueError("用户不存在")
        
        user.status = False
        await db.commit()
        await db.refresh(user)
        
        logger.info(f"用户已禁用: {user.id}")
        return user
    
    @staticmethod
    async def change_password(db: AsyncSession, user: User, old_password: str, new_password: str) -> bool:
        """修改密码"""
        if not verify_password(old_password, user.password):
            raise ValueError("旧密码不正确")
        
        user.password = get_password_hash(new_password)
        await db.commit()
        
        logger.info(f"用户密码修改: {user.id}")
        return True
    
    @staticmethod
    async def delete_user(db: AsyncSession, user_id: int) -> bool:
        """删除用户"""
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            raise ValueError("用户不存在")
        
        await db.delete(user)
        await db.commit()
        
        logger.info(f"用户已删除: {user_id}")
        return True
    
    @staticmethod
    async def update_user_password(db: AsyncSession, user_id: int, new_password: str) -> bool:
        """更新用户密码"""
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            raise ValueError("用户不存在")
        
        from app.core.security import get_password_hash
        user.password = get_password_hash(new_password)
        await db.commit()
        
        logger.info(f"用户密码已更新: {user_id}")
        return True
    
    @staticmethod
    async def request_password_reset(db: AsyncSession, email: str) -> tuple[bool, str]:
        """
        请求密码重置
        返回: (success, token_or_message)
        """
        user = await UserService.get_user_by_email(db, email)
        if not user:
            return False, "该邮箱未注册"
        
        import secrets
        token = secrets.token_urlsafe(32)
        user.password_reset_token = token
        user.password_reset_expires = datetime.utcnow() + timedelta(hours=1)
        await db.commit()
        
        # 发送密码重置邮件
        reset_link = f"http://localhost:3000/reset-password?token={token}"
        from app.services.email_service import EmailService
        EmailService.send_password_reset_email(email, reset_link)
        
        return True, token
    
    @staticmethod
    async def reset_password(db: AsyncSession, token: str, new_password: str) -> bool:
        """重置密码"""
        result = await db.execute(
            select(User).where(User.password_reset_token == token)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError("无效的重置链接")
        
        if datetime.utcnow() > user.password_reset_expires:
            raise ValueError("重置链接已过期")
        
        user.password = get_password_hash(new_password)
        user.password_reset_token = None
        user.password_reset_expires = None
        user.login_error_count = 0
        user.locked_until = None
        await db.commit()
        
        logger.info(f"密码重置成功: {user.email}")
        return True
    
    @staticmethod
    def mask_email(email: str) -> str:
        """邮箱脱敏显示"""
        if not email:
            return email
        if '@' not in email:
            return email
        parts = email.split('@')
        name = parts[0]
        domain = parts[1]
        if len(name) <= 2:
            masked_name = name[0] + '***'
        else:
            masked_name = name[0] + '***' + name[-1]
        return f"{masked_name}@{domain}"
    
    @staticmethod
    def mask_phone(phone: str) -> str:
        """手机号脱敏显示"""
        if not phone:
            return phone
        if len(phone) != 11:
            return phone
        return f"{phone[:3]}****{phone[-4:]}"