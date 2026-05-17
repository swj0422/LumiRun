from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
import re


def validate_password_strength(password: str) -> str:
    """验证密码强度：至少6位，包含大小写字母"""
    if len(password) < 6:
        raise ValueError('密码长度至少6位')
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    if not has_upper or not has_lower:
        raise ValueError('密码必须包含大写和小写字母')
    return password


class UserBase(BaseModel):
    """用户基础模型"""
    email: EmailStr = Field(..., description="邮箱（用于找回密码）")
    username: str = Field(..., min_length=3, max_length=50, description="用户名（登录账号）")
    real_name: str = Field(..., min_length=2, max_length=50, description="真实姓名")


class UserCreate(BaseModel):
    """用户注册模型"""
    email: EmailStr = Field(..., description="邮箱")
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=50, description="密码")
    real_name: str = Field(..., min_length=2, max_length=50, description="真实姓名")
    role_id: int = Field(..., description="角色ID：3-导师，4-学员")
    
    @validator('password')
    def validate_password(cls, v):
        return validate_password_strength(v)
    
    @validator('role_id')
    def validate_role(cls, v):
        if v <= 0:
            raise ValueError('角色ID必须为正整数')
        return v


class UserUpdate(BaseModel):
    """用户更新模型"""
    real_name: Optional[str] = Field(None, min_length=2, max_length=50)
    phone: Optional[str] = None
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('手机号格式不正确')
        return v


class UserResponse(BaseModel):
    """用户响应模型"""
    id: int
    email: str
    real_name: str
    phone: Optional[str]
    role_id: int
    role_name: str
    status: bool
    last_login_time: Optional[datetime]
    login_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """用户登录模型"""
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")
    captcha: Optional[str] = Field(None, description="图形验证码（连续错误3次后必填）")


class Token(BaseModel):
    """令牌模型"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class TokenData(BaseModel):
    """令牌数据模型"""
    user_id: Optional[int] = None
    role: Optional[str] = None


class PasswordChange(BaseModel):
    """密码修改模型"""
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=50, description="新密码")
    
    @validator('new_password')
    def validate_password(cls, v):
        return validate_password_strength(v)


class PasswordResetRequest(BaseModel):
    """密码重置请求模型"""
    email: EmailStr = Field(..., description="注册邮箱")


class PasswordReset(BaseModel):
    """密码重置模型"""
    token: str = Field(..., description="重置令牌")
    new_password: str = Field(..., min_length=6, max_length=50, description="新密码")
    
    @validator('new_password')
    def validate_password(cls, v):
        return validate_password_strength(v)


class CaptchaResponse(BaseModel):
    """验证码响应模型"""
    captcha_id: str = Field(..., description="验证码ID")
    captcha_image: str = Field(..., description="Base64编码的验证码图片")
