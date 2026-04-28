-- 更新用户邮箱为有效格式
USE lumirun;

-- 将临时邮箱改为有效格式
UPDATE sys_user SET email = CONCAT('user', id, '@example.com') WHERE email LIKE '%@temp.local';

-- 验证
SELECT id, email, real_name, role_id, status FROM sys_user;
