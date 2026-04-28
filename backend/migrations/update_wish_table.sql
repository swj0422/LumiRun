-- 更新心愿表结构
-- 1. 添加新字段
ALTER TABLE wish
ADD COLUMN title VARCHAR(100) COMMENT '心愿标题',
ADD COLUMN description TEXT COMMENT '心愿描述',
ADD COLUMN image_urls VARCHAR(500) COMMENT '图片URL，逗号分隔，最多3张',
ADD COLUMN teacher_comment TEXT COMMENT '导师回复',
ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '心愿更新时间';

-- 2. 修改 status 字段类型（从 BOOLEAN 改为 INT）
ALTER TABLE wish
MODIFY COLUMN status INT DEFAULT 0 COMMENT '心愿状态：0-待处理，1-已实现，2-已拒绝';

-- 3. 修改 created_at 默认值为当前时间
ALTER TABLE wish
MODIFY COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '心愿创建时间';

-- 4. 为没有标题的旧记录设置默认标题
UPDATE wish SET title = '未命名心愿' WHERE title IS NULL;

-- 5. 设置 title 为必填字段
ALTER TABLE wish
MODIFY COLUMN title VARCHAR(100) NOT NULL COMMENT '心愿标题';

-- 6. 删除不再需要的字段（可选，如果之前有 gift_id 和 notified_at 字段）
-- ALTER TABLE wish DROP COLUMN gift_id;
-- ALTER TABLE wish DROP COLUMN notified_at;

-- 7. 创建索引
CREATE INDEX idx_wish_user_id ON wish(user_id);
CREATE INDEX idx_wish_class_id ON wish(class_id);
CREATE INDEX idx_wish_status ON wish(status);