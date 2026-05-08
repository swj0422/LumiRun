-- 逐光成长系统权限数据初始化脚本
USE lumirun;

-- 权限表
CREATE TABLE IF NOT EXISTS sys_permission (
    id INT AUTO_INCREMENT PRIMARY KEY,
    permission_name VARCHAR(50) NOT NULL COMMENT '权限名称',
    permission_code VARCHAR(50) NOT NULL UNIQUE COMMENT '权限编码',
    parent_id INT COMMENT '父权限ID',
    type INT NOT NULL COMMENT '权限类型：1-菜单，2-按钮',
    path VARCHAR(255) COMMENT '路由路径',
    component VARCHAR(255) COMMENT '组件路径',
    icon VARCHAR(50) COMMENT '图标',
    sort INT DEFAULT 0 COMMENT '排序',
    status TINYINT(1) DEFAULT 1 COMMENT '状态：0-禁用，1-启用',
    FOREIGN KEY (parent_id) REFERENCES sys_permission(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 角色权限关联表
CREATE TABLE IF NOT EXISTS sys_role_permission (
    id INT AUTO_INCREMENT PRIMARY KEY,
    role_id INT NOT NULL COMMENT '角色ID',
    permission_id INT NOT NULL COMMENT '权限ID',
    FOREIGN KEY (role_id) REFERENCES sys_role(id),
    FOREIGN KEY (permission_id) REFERENCES sys_permission(id),
    UNIQUE KEY uk_role_permission (role_id, permission_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 插入权限数据
INSERT INTO sys_permission (id, permission_name, permission_code, parent_id, type, path, icon, sort) VALUES
-- 系统管理
(1, '系统管理', 'system', NULL, 1, '/admin', 'setting', 1),
(2, '用户管理', 'system:user', 1, 1, '/admin/users', 'users', 10),
(3, '用户列表', 'system:user:list', 2, 2, NULL, NULL, 1),
(4, '用户创建', 'system:user:create', 2, 2, NULL, NULL, 2),
(5, '用户编辑', 'system:user:edit', 2, 2, NULL, NULL, 3),
(6, '用户删除', 'system:user:delete', 2, 2, NULL, NULL, 4),

-- 角色管理
(7, '角色管理', 'system:role', 1, 1, '/admin/roles', 'user-role', 20),
(8, '角色列表', 'system:role:list', 7, 2, NULL, NULL, 1),
(9, '角色创建', 'system:role:create', 7, 2, NULL, NULL, 2),
(10, '角色编辑', 'system:role:edit', 7, 2, NULL, NULL, 3),
(11, '角色删除', 'system:role:delete', 7, 2, NULL, NULL, 4),
(12, '角色权限', 'system:role:permission', 7, 2, NULL, NULL, 5),

-- 权限管理
(13, '权限管理', 'system:permission', 1, 1, '/admin/permissions', 'lock', 30),
(14, '权限列表', 'system:permission:list', 13, 2, NULL, NULL, 1),

-- 心愿管理
(15, '心愿管理', 'system:wish', 1, 1, '/admin/wishes', 'heart', 40),
(16, '心愿列表', 'system:wish:list', 15, 2, NULL, NULL, 1),
(17, '心愿删除', 'system:wish:delete', 15, 2, NULL, NULL, 2),

-- 系统日志
(18, '系统日志', 'system:log', 1, 1, '/admin/logs', 'file-text', 50),
(19, '日志列表', 'system:log:list', 18, 2, NULL, NULL, 1),

-- 导师功能
(20, '班级管理', 'teacher:class', NULL, 1, '/teacher/classes', 'graduation-cap', 2),
(21, '班级列表', 'teacher:class:list', 20, 2, NULL, NULL, 1),
(22, '班级创建', 'teacher:class:create', 20, 2, NULL, NULL, 2),
(23, '班级编辑', 'teacher:class:edit', 20, 2, NULL, NULL, 3),
(24, '班级删除', 'teacher:class:delete', 20, 2, NULL, NULL, 4),

-- 成长值管理
(25, '成长值管理', 'teacher:growth', NULL, 1, '/teacher/growth', 'trending-up', 3),
(26, '成长值列表', 'teacher:growth:list', 25, 2, NULL, NULL, 1),
(27, '成长值添加', 'teacher:growth:add', 25, 2, NULL, NULL, 2),
(28, '成长原因', 'teacher:growth:reason', 25, 2, NULL, NULL, 3),

-- 礼品管理
(29, '礼品管理', 'teacher:gift', NULL, 1, '/teacher/gifts', 'gift', 4),
(30, '礼品列表', 'teacher:gift:list', 29, 2, NULL, NULL, 1),
(31, '礼品创建', 'teacher:gift:create', 29, 2, NULL, NULL, 2),
(32, '礼品编辑', 'teacher:gift:edit', 29, 2, NULL, NULL, 3),
(33, '礼品删除', 'teacher:gift:delete', 29, 2, NULL, NULL, 4),

-- 订单管理
(34, '订单管理', 'teacher:order', NULL, 1, '/teacher/orders', 'shopping-cart', 5),
(35, '订单列表', 'teacher:order:list', 34, 2, NULL, NULL, 1),
(36, '订单审核', 'teacher:order:audit', 34, 2, NULL, NULL, 2),
(37, '订单发货', 'teacher:order:delivery', 34, 2, NULL, NULL, 3),
(38, '订单核销', 'teacher:order:verify', 34, 2, NULL, NULL, 4),

-- 学员功能
(39, '我的成长', 'student:growth', NULL, 1, '/student/growth', 'chart-line', 1),
(40, '成长记录', 'student:growth:record', 39, 2, NULL, NULL, 1),

-- 心愿便利贴
(41, '心愿便利贴', 'wish', NULL, 1, '/wish-wall', 'heart', 10),
(42, '心愿发布', 'wish:create', 41, 2, NULL, NULL, 1),
(43, '心愿删除', 'wish:delete', 41, 2, NULL, NULL, 2)
ON DUPLICATE KEY UPDATE permission_name = VALUES(permission_name);

-- 为超级管理员分配所有权限
INSERT INTO sys_role_permission (role_id, permission_id)
SELECT 1, id FROM sys_permission
ON DUPLICATE KEY UPDATE role_id = VALUES(role_id);

-- 为管理员分配系统管理相关权限
INSERT INTO sys_role_permission (role_id, permission_id) VALUES
(2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6),
(2, 7), (2, 8), (2, 9), (2, 10), (2, 11), (2, 12),
(2, 13), (2, 14), (2, 15), (2, 16), (2, 17),
(2, 18), (2, 19), (2, 41), (2, 42), (2, 43)
ON DUPLICATE KEY UPDATE role_id = VALUES(role_id);

-- 为导师分配导师功能权限
INSERT INTO sys_role_permission (role_id, permission_id) VALUES
(3, 20), (3, 21), (3, 22), (3, 23), (3, 24),
(3, 25), (3, 26), (3, 27), (3, 28),
(3, 29), (3, 30), (3, 31), (3, 32), (3, 33),
(3, 34), (3, 35), (3, 36), (3, 37), (3, 38),
(3, 41), (3, 42), (3, 43)
ON DUPLICATE KEY UPDATE role_id = VALUES(role_id);

-- 为学员分配学员功能权限
INSERT INTO sys_role_permission (role_id, permission_id) VALUES
(4, 39), (4, 40), (4, 41), (4, 42), (4, 43)
ON DUPLICATE KEY UPDATE role_id = VALUES(role_id);

SELECT '权限数据初始化完成' AS result;