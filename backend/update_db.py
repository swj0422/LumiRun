import asyncio
from app.core.database import Base, engine, AsyncSessionLocal
from app.models.student_note import StudentNote

async def update_database():
    async with engine.begin() as conn:
        # 自动更新表结构
        await conn.run_sync(Base.metadata.create_all)
    print('数据库表结构更新完成')

if __name__ == '__main__':
    asyncio.run(update_database())