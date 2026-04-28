-- 用户表结构修改：支持邮箱登录
-- 执行前请备份数据

USE lumirun;

-- 1. 添加新字段
ALTER TABLE sys_user ADD COLUMN email VARCHAR(100) COMMENT '邮箱（登录账号）' AFTER id;
ALTER TABLE sys_user ADD COLUMN login_error_count INT DEFAULT 0 COMMENT '连续登录错误次数' AFTER login_count;
ALTER TABLE sys_user ADD COLUMN locked_until DATETIME NULL COMMENT '账号锁定截止时间' AFTER login_error_count;
ALTER TABLE sys_user ADD COLUMN password_reset_token VARCHAR(100) NULL COMMENT '密码重置令牌' AFTER locked_until;
ALTER TABLE sys_user ADD COLUMN password_reset_expires DATETIME NULL COMMENT '密码重置令牌过期时间' AFTER password_reset_token;

-- 2. 将现有phone数据迁移到email（临时处理）
UPDATE sys_user SET email = CONCAT(phone, '@temp.local') WHERE email IS NULL;

-- 3. 修改phone字段允许为空
ALTER TABLE sys_user MODIFY COLUMN phone VARCHAR(20) NULL COMMENT '手机号（选填）';

-- 4. 删除phone的唯一约束（如果存在）
ALTER TABLE sys_user DROP INDEX phone;

-- 5. 添加email唯一约束
ALTER TABLE sys_user ADD UNIQUE INDEX idx_email (email);

-- 6. 删除username的唯一约束（如果存在）
ALTER TABLE sys_user DROP INDEX username;

-- 7. 验证结果
SELECT id, email, real_name, phone, role_id, status FROM sys_user LIMIT 10;
