import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler
from app.core.config import get_settings

settings = get_settings()


def setup_logger():
    """配置日志（Windows兼容）"""
    # 创建日志目录（使用Path确保跨平台兼容）
    log_file = Path(settings.LOG_FILE)
    log_dir = log_file.parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 配置根日志记录器
    logger = logging.getLogger("lumirun")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # 清除现有处理器
    logger.handlers.clear()
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # 文件处理器（Windows兼容）
    if settings.LOG_FILE:
        try:
            file_handler = RotatingFileHandler(
                str(settings.LOG_FILE),
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5,
                encoding="utf-8"
            )
            file_handler.setLevel(logging.INFO)
            file_format = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
            )
            file_handler.setFormatter(file_format)
            logger.addHandler(file_handler)
        except Exception as e:
            # 文件日志创建失败时，只使用控制台日志
            logger.warning(f"无法创建文件日志处理器: {e}")
    
    return logger


# 全局日志实例
logger = setup_logger()
