from datetime import datetime, timedelta
from typing import Optional, Union, Any, Tuple, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import get_settings
from app.core.database import get_db, AsyncSessionLocal
from app.models.user import User
from app.core.logger import logger


class TokenData:
    def __init__(self, user_id: int):
        self.user_id = user_id

settings = get_settings()
pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    return pwd_context.hash(password)


def validate_password_strength(password: str) -> bool:
    """验证密码强度
    密码规则：
    - 至少8位
    - 包含大小写字母
    - 包含数字
    - 包含特殊字符
    """
    import re
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    return True


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建JWT访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建JWT刷新令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # 刷新令牌有效期更长，例如7天
        expire = datetime.utcnow() + timedelta(days=7)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_current_user_from_token(token: str) -> Optional[User]:
    """从token获取当前用户（用于WebSocket）"""
    from app.core.database import async_session
    from app.models.user import User
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        token_data = TokenData(user_id=int(user_id))
    except (JWTError, ValueError):
        return None
    
    async with AsyncSessionLocal() as db:
        user = await db.get(User, token_data.user_id)
        if user is None:
            return None
        return user


def decode_token(token: str) -> Optional[dict]:
    """解码JWT令牌"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


from fastapi import Request

async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> User:
    """获取当前登录用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 从请求头中获取 token
        token = None
        authorization = request.headers.get("Authorization")
        if authorization and authorization.startswith("Bearer "):
            token = authorization.split(" ")[1]
            logger.info(f"[DEBUG] 从 Authorization 头中获取 token: {token[:50]}...")
        
        # 如果请求头中没有 token，从 Cookie 中获取
        if not token:
            try:
                if request.cookies:
                    token = request.cookies.get("token")
                    logger.info(f"[DEBUG] 从 Cookie 中获取 token: {token[:50]}..." if token else "[DEBUG] Cookie 中没有 token")
                else:
                    logger.info("[DEBUG] 请求中没有 Cookie")
            except Exception as e:
                logger.info(f"[DEBUG] 从 Cookie 中获取 token 失败: {e}")
        
        # 打印所有请求头和 Cookie，以便调试
        try:
            logger.info(f"[DEBUG] All request headers: {dict(request.headers) if request.headers else {}}")
        except Exception as e:
            logger.info(f"[DEBUG] Failed to log headers: {e}")
        try:
            logger.info(f"[DEBUG] All request cookies: {dict(request.cookies) if request.cookies else {}}")
        except Exception as e:
            logger.info(f"[DEBUG] Failed to log cookies: {e}")
        
        if not token:
            logger.error("[DEBUG] 没有找到 token")
            raise credentials_exception
        
        payload = decode_token(token)
        if payload is None:
            logger.error(f"[DEBUG] Token 解码失败")
            raise credentials_exception
        
        logger.info(f"[DEBUG] Token payload: {payload}")
        
        user_id: str = payload.get("sub")
        if user_id is None:
            logger.error(f"[DEBUG] Token 中没有 sub 字段")
            raise credentials_exception
        
        logger.info(f"[DEBUG] User ID: {user_id}")
        
        # 从数据库获取用户（预加载role关系）
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        result = await db.execute(
            select(User).options(selectinload(User.role)).where(User.id == int(user_id))
        )
        user = result.scalar_one_or_none()
        
        logger.info(f"[DEBUG] User from DB: {user}")
        
        if user is None:
            logger.error(f"[DEBUG] User not found in database")
            raise credentials_exception
        
        if not user.status:
            logger.error(f"[DEBUG] User status is False")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="账号已被禁用"
            )
        
        logger.info(f"[DEBUG] User authenticated successfully: {user.real_name}")
        return user
    except HTTPException as e:
        # 重新抛出HTTPException，保持原有状态码
        raise
    except Exception as e:
        logger.error(f"[DEBUG] get_current_user 错误: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="认证服务错误"
        )


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """获取当前活跃用户"""
    return current_user


# 角色检查依赖
def require_role(*roles: str):
    """要求特定角色的依赖"""
    async def role_checker(current_user: User = Depends(get_current_user)):
        if not current_user.role or current_user.role.role_name not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        return current_user
    return role_checker


# 常用角色依赖
require_admin = require_role("super_admin", "admin")
require_teacher = require_role("super_admin", "admin", "teacher", "class_assistant")
require_manager = require_teacher  # 别名，兼容术语替换
require_student = require_role("student")
require_member = require_student  # 别名，兼容术语替换


async def require_class_assistant(
    class_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> User:
    """要求用户是指定班级的助理"""
    from app.services.class_assistant_service import ClassAssistantService
    
    is_assistant = await ClassAssistantService.is_assistant_of_class(db, current_user.id, class_id)
    if not is_assistant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限操作此班级"
        )
    return current_user


async def require_growth_permission(
    class_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Tuple[bool, Optional[List[int]]]:
    """
    要求成长值操作权限的依赖注入
    
    返回: (is_teacher, assistant_class_ids)
    """
    from app.core.permission import PermissionChecker
    
    return await PermissionChecker.require_growth_permission(db, current_user, class_id)
