-- 修复角色名称编码问题，改为英文
USE lumirun;

-- 更新角色名称为英文
UPDATE sys_role SET role_name = 'super_admin', remark = '系统最高权限，可管理所有功能' WHERE id = 1;
UPDATE sys_role SET role_name = 'admin', remark = '管理用户和日志，不可操作业务数据' WHERE id = 2;
UPDATE sys_role SET role_name = 'teacher', remark = '管理班级、学员、成长值、奖励' WHERE id = 3;
UPDATE sys_role SET role_name = 'student', remark = '查看成长值、兑换奖励' WHERE id = 4;

-- 验证
SELECT id, role_name, remark FROM sys_role;
