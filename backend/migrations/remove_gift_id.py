import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+aiomysql://lumirun:lumirunpassword@localhost:3306/lumirun?charset=utf8mb4")
sync_url = DATABASE_URL.replace("aiomysql", "pymysql")
engine = create_engine(sync_url)

with engine.connect() as conn:
    print("Removing gift_id foreign key constraint and column...")
    
    # 删除外键约束
    conn.execute(text("ALTER TABLE wish DROP FOREIGN KEY wish_ibfk_2"))
    
    # 删除 gift_id 字段
    conn.execute(text("ALTER TABLE wish DROP COLUMN gift_id"))
    
    conn.commit()
    print("Done!")