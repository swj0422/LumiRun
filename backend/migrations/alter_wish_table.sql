-- 修改心愿表结构以支持心愿便利贴功能
-- 1. 删除旧字段（如果存在）
ALTER TABLE wish DROP COLUMN IF EXISTS title;
ALTER TABLE wish DROP COLUMN IF EXISTS description;
ALTER TABLE wish DROP COLUMN IF EXISTS image_urls;
ALTER TABLE wish DROP COLUMN IF EXISTS status;
ALTER TABLE wish DROP COLUMN IF EXISTS teacher_comment;
ALTER TABLE wish DROP COLUMN IF EXISTS updated_at;

-- 2. 添加新字段
ALTER TABLE wish ADD COLUMN IF NOT EXISTS content VARCHAR(200) NOT NULL DEFAULT '' COMMENT '心愿文字内容（1-200字）';
ALTER TABLE wish ADD COLUMN IF NOT EXISTS image_url VARCHAR(255) NULL COMMENT '图片地址';
ALTER TABLE wish ADD COLUMN IF NOT EXISTS is_anonymous TINYINT(1) DEFAULT 0 NOT NULL COMMENT '是否匿名：1-匿名，0-不匿名';
ALTER TABLE wish ADD COLUMN IF NOT EXISTS is_deleted TINYINT(1) DEFAULT 0 NOT NULL COMMENT '是否已删除：0-正常，1-已删除';

-- 3. 删除不需要的索引
ALTER TABLE wish DROP INDEX IF EXISTS idx_wish_user_id;
ALTER TABLE wish DROP INDEX IF EXISTS idx_wish_class_student_id;
ALTER TABLE wish DROP INDEX IF EXISTS idx_wish_created_at;

-- 4. 添加新索引
CREATE INDEX IF NOT EXISTS idx_wish_user_id ON wish(user_id);
CREATE INDEX IF NOT EXISTS idx_wish_class_student_id ON wish(class_student_id);
CREATE INDEX IF NOT EXISTS idx_wish_created_at ON wish(created_at);