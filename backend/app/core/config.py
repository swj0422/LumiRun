from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "LumiRun"
    APP_NAME_CN: str = "逐光成长系统"
    DEBUG: bool = False
    VERSION: str = "1.0.0"
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    
    # 数据库配置
    DATABASE_URL: str = "mysql+aiomysql://root:your-sql-password@localhost:3306/lumirun?charset=utf8mb4"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_POOL_SIZE: int = 10
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天
    
    # 文件上传配置（Windows兼容路径）
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES: list = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    
    # 分页配置
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # 缓存配置
    CACHE_EXPIRE_SECONDS: int = 300  # 5分钟
    
    # 日志配置（Windows兼容路径）
    LOG_DIR: Path = BASE_DIR / "logs"
    LOG_FILE: Path = LOG_DIR / "lumirun.log"
    LOG_LEVEL: str = "INFO"
    
    # 第三方集成配置（后期扩展）
    WEWORK_CORP_ID: Optional[str] = None
    WEWORK_SECRET: Optional[str] = None
    WEWORK_AGENT_ID: Optional[str] = None
    
    # 邮件发送配置
    SMTP_SERVER: str = "smtp.sina.com"
    SMTP_PORT: int = 465
    SMTP_USER: str = "lumirun@sina.com"
    SMTP_PASSWORD: str = "your-smtp-password"
    SMTP_FROM: str = "lumirun@sina.com"
    SMTP_USE_TLS: bool = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 确保目录存在
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
