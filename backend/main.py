from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.core.config import get_settings
from app.core.database import init_db, close_db
from app.api.v1 import api_router
from app.core.logger import logger
from app.core.middleware import PerformanceMonitorMiddleware, ErrorHandlerMiddleware
import os
# 导入所有模型，确保数据库表被创建
from app.models import *

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info(f"Starting {settings.APP_NAME} v{settings.VERSION}")
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}", exc_info=True)
        raise
    
    yield
    
    # 关闭时
    try:
        await close_db()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Database close failed: {e}")
    logger.info("Application shutdown")


app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_NAME_CN,
    version=settings.VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应配置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 性能监控中间件
app.add_middleware(PerformanceMonitorMiddleware)

# 错误处理中间件
app.add_middleware(ErrorHandlerMiddleware)

# 配置静态文件服务
frontend_build_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")

# 注册路由
app.include_router(api_router, prefix="/api/v1")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": f"服务器内部错误: {str(exc)}"}
    )


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


# 挂载上传文件服务
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
logger.info(f"Upload files mounted from: {settings.UPLOAD_DIR}")

# 路由回退，处理 SPA 路由
@app.get("/{path:path}")
async def fallback(path: str):
    """前端路由回退"""
    if os.path.exists(frontend_build_dir):
        index_path = os.path.join(frontend_build_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
    return JSONResponse(
        status_code=404,
        content={"detail": "Not Found"}
    )

# 挂载静态文件服务（放在最后，确保 API 路由优先）
if os.path.exists(frontend_build_dir):
    static_dir = os.path.join(frontend_build_dir, "static")
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
        logger.info(f"Static files mounted from: {static_dir}")
    else:
        logger.warning(f"Static directory not found: {static_dir}")
    logger.info(f"Frontend build directory found: {frontend_build_dir}")
else:
    logger.warning(f"Frontend build directory not found: {frontend_build_dir}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else 4
    )
