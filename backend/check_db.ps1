# 检查数据库连接和日志表
cd "d:\LumiRun\LumiRun\backend"
python -c "
import asyncio
from app.core.database import AsyncSessionLocal
from app.models.student_operation_log import StudentOperationLog
from sqlalchemy import select

async def check_db():
    try:
        print('Connecting to database...')
        async with AsyncSessionLocal() as db:
            print('Checking student_operation_log table...')
            result = await db.execute(select(StudentOperationLog).limit(5))
            logs = result.scalars().all()
            print(f'Number of logs in table: {len(logs)}')
            for log in logs:
                print(f'  - {log.created_at}: {log.operation_content}')
    except Exception as e:
        print(f'Error: {str(e)}')

asyncio.run(check_db())
"