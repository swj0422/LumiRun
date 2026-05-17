from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token, get_current_user, get_password_hash, validate_password_strength
from app.core.config import get_settings
from app.schemas.user import (
    UserCreate, UserLogin, Token, UserResponse, 
    PasswordResetRequest, PasswordReset, CaptchaResponse
)
from app.services.user_service import UserService
from app.services.captcha_service import CaptchaService
from app.models.user import User

router = APIRouter()
settings = get_settings()


@router.post("/register", response_model=dict)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """用户注册"""
    try:
        role = await UserService.get_role_by_id(db, user_data.role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="角色不存在"
            )
        
        is_approved = role.role_name == "student"
        
        user = await UserService.create_user(db, user_data, is_approved)
        
        return {
            "message": "注册成功" + ("，请等待管理员审核" if not is_approved else ""),
            "user_id": user.id,
            "need_approval": not is_approved
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/captcha", response_model=CaptchaResponse)
async def get_captcha():
    """获取图形验证码"""
    captcha_id, captcha_text, img_bytes = CaptchaService.generate_captcha()
    captcha_image = CaptchaService.get_captcha_base64(captcha_id, img_bytes)
    
    return {
        "captcha_id": captcha_id,
        "captcha_image": captcha_image
    }


@router.post("/login", response_model=dict)
async def login(
    login_data: UserLogin,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """用户登录"""
    try:
        captcha_id = request.headers.get("X-Captcha-Id")
        
        user, error = await UserService.authenticate_user(
            db, 
            login_data.username, 
            login_data.password,
            login_data.captcha,
            captcha_id
        )
        
        if error == "NEED_CAPTCHA":
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="需要验证码"
            )
        
        if error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=error
            )
        
        if not user.status:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="账号未激活，请等待管理员审核"
            )
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role.role_name},
            expires_delta=access_token_expires
        )
        
        # 创建刷新令牌
        refresh_token = create_refresh_token(
            data={"sub": str(user.id), "role": user.role.role_name}
        )
        
        # 设置HttpOnly Cookie
        response.set_cookie(
            key="token",
            value=access_token,
            httponly=True,
            secure=not settings.DEBUG,  # 根据环境动态设置secure
            samesite="strict" if not settings.DEBUG else "lax",  # 生产环境使用strict
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            path="/"  # 设置Cookie的路径为根路径，这样所有接口都能访问到
        )
        
        user_data = {
            "id": user.id,
            "email": UserService.mask_email(user.email),
            "real_name": user.real_name,
            "phone": user.phone,
            "role_id": user.role_id,
            "role_name": user.role.role_name if user.role else "未知",
            "status": user.status,
            "last_login_time": user.last_login_time.isoformat() if user.last_login_time else None,
            "login_count": user.login_count,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }

        # 获取用户的助理班级授权信息
        from app.services.class_assistant_service import ClassAssistantService
        assistant_classes = await ClassAssistantService.get_user_assistant_classes(db, user.id)
        assistant_class_ids = [cls.id for cls in assistant_classes]

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": user_data,
            "is_class_assistant": len(assistant_class_ids) > 0,
            "assistant_classes": assistant_class_ids
        }
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登录失败: {str(e)}"
        )


@router.get("/me", response_model=dict)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """获取当前用户信息"""
    return {
        "id": current_user.id,
        "email": UserService.mask_email(current_user.email),
        "real_name": current_user.real_name,
        "phone": UserService.mask_phone(current_user.phone),
        "role_id": current_user.role_id,
        "role_name": current_user.role.role_name if current_user.role else "未知",
        "status": current_user.status,
        "last_login_time": current_user.last_login_time.isoformat() if current_user.last_login_time else None,
        "login_count": current_user.login_count,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None
    }


@router.post("/forgot-password", response_model=dict)
async def forgot_password(
    data: PasswordResetRequest,
    db: AsyncSession = Depends(get_db)
):
    """忘记密码 - 发送重置链接"""
    success, result = await UserService.request_password_reset(db, data.email)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result
        )
    
    return {
        "message": "重置链接已发送到您的邮箱，请查收"
    }


@router.post("/reset-password", response_model=dict)
async def reset_password(
    data: PasswordReset,
    db: AsyncSession = Depends(get_db)
):
    """重置密码"""
    try:
        await UserService.reset_password(db, data.token, data.new_password)
        return {"message": "密码重置成功，请使用新密码登录"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/refresh-token", response_model=dict)
async def refresh_token(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """刷新访问令牌"""
    try:
        # 从请求头获取刷新令牌
        refresh_token = request.headers.get("Authorization")
        if not refresh_token or not refresh_token.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="缺少有效的刷新令牌"
            )
        
        refresh_token = refresh_token.split(" ")[1]
        
        # 验证刷新令牌
        from jose import jwt, JWTError
        from app.core.config import get_settings
        settings = get_settings()
        
        try:
            payload = jwt.decode(
                refresh_token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            
            # 检查令牌类型
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="无效的刷新令牌"
                )
            
            user_id = payload.get("sub")
            role_name = payload.get("role")
            
            if not user_id or not role_name:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="无效的刷新令牌"
                )
                
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的刷新令牌"
            )
        
        # 验证用户是否存在
        user = await db.get(User, int(user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在"
            )
        
        # 生成新的访问令牌
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role.role_name},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"刷新令牌失败: {str(e)}"
        )
