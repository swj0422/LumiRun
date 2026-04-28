import asyncio
from app.core.database import engine, Base
from app.models import StudentOperationLog

async def init_database():
    """初始化数据库表"""
    try:
        async with engine.begin() as conn:
            # 重新创建表
            await conn.run_sync(Base.metadata.create_all, checkfirst=True)
        print("Database tables initialized successfully")
    except Exception as e:
        print(f"Failed to initialize database tables: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(init_database())
