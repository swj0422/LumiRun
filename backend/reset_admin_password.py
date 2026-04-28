from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.security import get_password_hash
from app.models.user import User
from app.core.config import get_settings

async def reset_admin_password():
    settings = get_settings()
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # 获取admin用户
        from sqlalchemy import select
        result = await session.execute(select(User).where(User.username == 'admin'))
        user = result.scalar_one_or_none()
        
        if user:
            # 重置密码为123456
            user.password = get_password_hash('123456')
            await session.commit()
            print("Admin password reset successfully to '123456'")
        else:
            print("Admin user not found")
    
    await engine.dispose()

if __name__ == "__main__":
    import asyncio
    asyncio.run(reset_admin_password())
