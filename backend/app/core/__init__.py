from app.core.config import get_settings, Settings
from app.core.database import get_db, init_db, close_db, Base
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_token,
    get_current_user,
    get_current_active_user,
    require_role,
    require_admin,
    require_teacher,
    require_student,
)
from app.core.cache import cache, cache_result, CacheManager
from app.core.logger import logger, setup_logger

__all__ = [
    "get_settings",
    "Settings",
    "get_db",
    "init_db",
    "close_db",
    "Base",
    "verify_password",
    "get_password_hash",
    "create_access_token",
    "decode_token",
    "get_current_user",
    "get_current_active_user",
    "require_role",
    "require_admin",
    "require_teacher",
    "require_student",
    "cache",
    "cache_result",
    "CacheManager",
    "logger",
    "setup_logger",
]
