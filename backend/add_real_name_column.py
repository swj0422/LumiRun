import asyncio
from app.core.database import engine
from sqlalchemy import text

async def add_real_name_column():
    async with engine.begin() as conn:
        # 检查 student_note 表是否存在 real_name 字段
        result = await conn.execute(text("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'lumirun' 
            AND TABLE_NAME = 'student_note' 
            AND COLUMN_NAME = 'real_name'
        """))
        
        if not result.fetchone():
            # 添加 real_name 字段
            await conn.execute(text("""
                ALTER TABLE student_note 
                ADD COLUMN real_name VARCHAR(50) NULL COMMENT '真实姓名' AFTER class_student_id
            """))
            print('成功添加 real_name 字段到 student_note 表')
        else:
            print('real_name 字段已经存在')

if __name__ == '__main__':
    asyncio.run(add_real_name_column())