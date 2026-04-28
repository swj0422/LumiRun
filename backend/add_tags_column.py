import asyncio
from app.core.database import engine
from sqlalchemy import text

async def add_tags_column():
    async with engine.begin() as conn:
        result = await conn.execute(text("""
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = 'lumirun'
            AND TABLE_NAME = 'student_note'
            AND COLUMN_NAME = 'tags'
        """))

        if not result.fetchone():
            await conn.execute(text("""
                ALTER TABLE student_note
                ADD COLUMN tags TEXT NULL COMMENT '标签JSON' AFTER performance_summary
            """))
            print('成功添加 tags 字段到 student_note 表')
        else:
            print('tags 字段已经存在')

if __name__ == '__main__':
    asyncio.run(add_tags_column())