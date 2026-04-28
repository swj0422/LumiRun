-- 班级学员表结构迁移
-- 1. 添加 is_active 字段
ALTER TABLE `class_student` ADD COLUMN `is_active` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否启用：1-启用，0-停用' AFTER `is_deleted`;

-- 2. 将所有 is_deleted=0 的记录的 is_active 设置为 1（默认启用）
UPDATE `class_student` SET `is_active` = 1 WHERE `is_deleted` = 0;

-- 3. 将状态为 'removed' 的记录标记为已删除（is_deleted=1）
UPDATE `class_student` SET `is_deleted` = 1 WHERE `bind_status` = 'removed';

-- 4. 将状态为 'stopped' 的记录停用（is_active=0）
UPDATE `class_student` SET `is_active` = 0 WHERE `bind_status` = 'stopped';

-- 5. 删除 remove_reason 字段（不再需要）
ALTER TABLE `class_student` DROP COLUMN `remove_reason`;

-- 6. 查看修改后的表结构
DESCRIBE `class_student`;