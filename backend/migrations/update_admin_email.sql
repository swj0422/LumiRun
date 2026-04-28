-- 更新管理员账号为邮箱登录
USE lumirun;

-- 更新管理员邮箱
UPDATE sys_user SET email = 'admin@lumirun.com' WHERE id = 5;

-- 验证
SELECT id, email, real_name, role_id, status FROM sys_user WHERE id = 5;
