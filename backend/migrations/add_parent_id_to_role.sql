-- 为角色表添加parent_id字段
USE lumirun;

-- 添加parent_id字段
ALTER TABLE sys_role 
ADD COLUMN parent_id INT NULL COMMENT '父角色ID';

-- 添加外键约束
ALTER TABLE sys_role 
ADD CONSTRAINT fk_sys_role_parent_id FOREIGN KEY (parent_id) REFERENCES sys_role(id);

-- 添加索引
ALTER TABLE sys_role 
ADD INDEX idx_parent_id (parent_id);

SELECT 'parent_id字段添加完成' AS result;