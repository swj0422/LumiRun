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
    print("Adding new columns to wish table...")
    
    conn.execute(text("ALTER TABLE wish ADD COLUMN title VARCHAR(100)"))
    conn.execute(text("ALTER TABLE wish ADD COLUMN description TEXT"))
    conn.execute(text("ALTER TABLE wish ADD COLUMN image_urls VARCHAR(500)"))
    conn.execute(text("ALTER TABLE wish ADD COLUMN teacher_comment TEXT"))
    conn.execute(text("ALTER TABLE wish ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    
    conn.execute(text("ALTER TABLE wish MODIFY COLUMN status INT DEFAULT 0"))
    conn.execute(text("ALTER TABLE wish MODIFY COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP"))
    conn.execute(text("UPDATE wish SET title = 'Unnamed Wish' WHERE title IS NULL"))
    conn.execute(text("ALTER TABLE wish MODIFY COLUMN title VARCHAR(100) NOT NULL"))
    
    conn.execute(text("CREATE INDEX idx_wish_user_id ON wish(user_id)"))
    conn.execute(text("CREATE INDEX idx_wish_class_id ON wish(class_id)"))
    conn.execute(text("CREATE INDEX idx_wish_status ON wish(status)"))
    
    conn.commit()
    print("Migration completed successfully!")