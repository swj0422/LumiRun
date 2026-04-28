import asyncio
from app.core.database import AsyncSessionLocal
from sqlalchemy import text

async def add_class_assistant_role():
    try:
        async with AsyncSessionLocal() as db:
            async with db.begin():
                # 检查是否已经存在 class_assistant 角色
                result = await db.execute(text("SELECT id FROM sys_role WHERE role_name = 'class_assistant'"))
                role = result.fetchone()
                
                if not role:
                    # 添加 class_assistant 角色
                    await db.execute(text("INSERT INTO sys_role (role_name, remark) VALUES ('class_assistant', '班级助理，协助导师管理班级')"))
                    print('添加 class_assistant 角色成功')
                    
                    # 获取新角色的ID
                    result = await db.execute(text("SELECT id FROM sys_role WHERE role_name = 'class_assistant'"))
                    role = result.fetchone()
                
                if role:
                    # 更新 assistant@example.com 的角色为 class_assistant
                    await db.execute(text("UPDATE sys_user SET role_id = :role_id WHERE email = 'assistant@example.com'"), {
                        'role_id': role[0]
                    })
                    print('更新助理账号角色成功')
                
                # 验证更新结果
                result = await db.execute(text("SELECT u.id, u.email, u.real_name, u.role_id, r.role_name FROM sys_user u JOIN sys_role r ON u.role_id = r.id WHERE u.email = 'assistant@example.com'"))
                user = result.fetchone()
                print('更新后的助理用户信息:')
                print(user)
    except Exception as e:
        print(f'Error: {str(e)}')

if __name__ == '__main__':
    asyncio.run(add_class_assistant_role())