-- 清空现有权限数据
DELETE FROM sys_role_permission;
DELETE FROM sys_permission;

-- 重置自增ID
ALTER TABLE sys_permission AUTO_INCREMENT = 1;

-- =============================================
-- 一、菜单权限（type=1）
-- =============================================

-- 1. 控制台（首页）
INSERT INTO sys_permission (id, permission_name, permission_code, parent_id, type, path, component, icon, sort, status) VALUES
(1, '控制台', 'menu:dashboard', NULL, 1, '/admin', 'Dashboard', 'HomeOutlined', 1, 1);

-- 2. 用户管理
INSERT INTO sys_permission (id, permission_name, permission_code, parent_id, type, path, component, icon, sort, status) VALUES
(2, '用户管理', 'menu:user', NULL, 1, '/admin/users', 'UserList', 'UserOutlined', 2, 1);

-- 3. 角色管理
INSERT INTO sys_permission (id, permission_name, permission_code, parent_id, type, path, component, icon, sort, status) VALUES
(3, '角色管理', 'menu:role', NULL, 1, '/admin/roles', 'RoleList', 'TeamOutlined', 3, 1);

-- 4. 权限管理
INSERT INTO sys_permission (id, permission_name, permission_code, parent_id, type, path, component, icon, sort, status) VALUES
(4, '权限管理', 'menu:permission', NULL, 1, '/admin/permissions', 'PermissionList', 'LockOutlined', 4, 1);

-- 5. 班级管理
INSERT INTO sys_permission (id, permission_name, permission_code, parent_id, type, path, component, icon, sort, status) VALUES
(5, '班级管理', 'menu:class', NULL, 1, '/admin/classes', 'ClassList', 'BankOutlined', 5, 1);

-- 6. 学员管理
INSERT INTO sys_permission (id, permission_name, permission_code, parent_id, type, path, component, icon, sort, status) VALUES
(6, '学员管理', 'menu:student', NULL, 1, '/admin/students', 'StudentList', 'SolutionOutlined', 6, 1);

-- 7. 礼品管理
INSERT INTO sys_permission (id, permission_name, permission_code, parent_id, type, path, component, icon, sort, status) VALUES
(7, '礼品管理', 'menu:gift', NULL, 1, '/admin/gifts', 'GiftList', 'GiftOutlined', 7, 1);

-- 8. 订单管理
INSERT INTO sys_permission (id, permission_name, permission_code, parent_id, type, path, component, icon, sort, status) VALUES
(8, '订单管理', 'menu:order', NULL, 1, '/admin/orders', 'OrderList', 'ShoppingOutlined', 8, 1);

-- 9. 心愿便利贴管理
INSERT INTO sys_permission (id, permission_name, permission_code, parent_id, type, path, component, icon, sort, status) VALUES
(9, '心愿便利贴管理', 'menu:wish', NULL, 1, '/admin/wishes', 'WishList', 'HeartOutlined', 9, 1);

-- 10. 意见征集管理
INSERT INTO sys_permission (id, permission_name, permission_code, parent_id, type, path, component, icon, sort, status) VALUES
(10, '意见征集管理', 'menu:suggestion', NULL, 1, '/admin/suggestions', 'SuggestionList', 'CommentOutlined', 10, 1);

-- 11. 系统日志
INSERT INTO sys_permission (id, permission_name, permission_code, parent_id, type, path, component, icon, sort, status) VALUES
(11, '系统日志', 'menu:log', NULL, 1, '/admin/logs', 'LogList', 'FileTextOutlined', 11, 1);

-- 12. 系统设置
INSERT INTO sys_permission (id, permission_name, permission_code, parent_id, type, path, component, icon, sort, status) VALUES
(12, '系统设置', 'menu:settings', NULL, 1, '/admin/settings', 'Settings', 'SettingOutlined', 12, 1);

-- =============================================
-- 二、按钮权限（type=2）
-- =============================================

-- 1. 控制台按钮权限
INSERT INTO sys_permission (id, permission_name, permission_code, parent_id, type, path, component, icon, sort, status) VALUES
(101, '查看统计', 'btn:dashboard:view', 1, 2, NULL, NULL, NULL, 1, 1);

-- 2. 用户管理按钮权限
INSERT INTO sys_permission (id, permission_name, permission_code, parent_id, type, path, component, icon, sort, status) VALUES
(201, '查看用户', 'btn:user:view', 2, 2, NULL, NULL, NULL, 1, 1),
(202, '编辑用户', 'btn:user:edit', 2, 2, NULL, NULL, NULL, 2, 1),
(203, '禁用用户', 'btn:user:disable', 2, 2, NULL, NULL, NULL, 3, 1),
(204, '启用用户', 'btn:user:enable', 2, 2, NULL, NULL, NULL, 4, 1),
(205, '重置密码', 'btn:user:reset-password', 2, 2, NULL, NULL, NULL, 5, 1),
(206, '编辑角色', 'btn:user:edit-role', 2, 2, NULL, NULL, NULL, 6, 1),
(207, '导出用户', 'btn:user:export', 2, 2, NULL, NULL, NULL, 7, 1);

-- 3. 角色管理按钮权限
INSERT INTO sys_permission (id, permission_name, permission_code, parent_id, type, path, component, icon, sort, status) VALUES
(301, '查看角色', 'btn:role:view', 3, 2, NULL, NULL, NULL, 1, 1),
(302, '创建角色', 'btn:role:create', 3, 2, NULL, NULL, NULL, 2, 1),
(303, '编辑角色', 'btn:role:edit', 3, 2, NULL, NULL, NULL, 3, 1),
(304, '删除角色', 'btn:role:delete', 3, 2, NULL, NULL, NULL, 4, 1),
(305, '分配权限', 'btn:role:assign-permission', 3, 2, NULL, NULL, NULL, 5, 1);

-- 4. 权限管理按钮权限
INSERT INTO sys_permission (id, permission_name, permission_code, parent_id, type, path, component, icon, sort, status) VALUES
(401, '查看权限', 'btn:permission:view', 4, 2, NULL, NULL, NULL, 1, 1),
(402, '创建权限', 'btn:permission:create', 4, 2, NULL, NULL, NULL, 2, 1),
(403, '编辑权限', 'btn:permission:edit', 4, 2, NULL, NULL, NULL, 3, 1),
(404, '删除权限', 'btn:permission:delete', 4, 2, NULL, NULL, NULL, 4, 1);

-- 5. 班级管理按钮权限
INSERT INTO sys_permission (id, permission_name, permission_code, parent_id, type, path, component, icon, sort, status) VALUES
(501, '查看班级', 'btn:class:view', 5, 2, NULL, NULL, NULL, 1, 1),
(502, '查看学员', 'btn:class:view-students', 5, 2, NULL, NULL, NULL, 2, 1),
(503, '查看成长记录', 'btn:class:view-growth', 5, 2, NULL, NULL, NULL, 3, 1),
(504, '关闭班级', 'btn:class:close', 5, 2, NULL, NULL, NULL, 4, 1),
(505, '开放班级', 'btn:class:open', 5, 2, NULL, NULL, NULL, 5, 1),
(506, '删除班级', 'btn:class:delete', 5, 2, NULL, NULL, NULL, 6, 1),
(507, '导出班级', 'btn:class:export', 5, 2, NULL, NULL, NULL, 7, 1);

-- 6. 学员管理按钮权限
INSERT INTO sys_permission (id, permission_name, permission_code, parent_id, type, path, component, icon, sort, status) VALUES
(601, '查看学员', 'btn:student:view', 6, 2, NULL, NULL, NULL, 1, 1),
(602, '查看详情', 'btn:student:view-detail', 6, 2, NULL, NULL, NULL, 2, 1),
(603, '查看成长记录', 'btn:student:view-growth', 6, 2, NULL, NULL, NULL, 3, 1),
(604, '强制解绑', 'btn:student:unbind', 6, 2, NULL, NULL, NULL, 4, 1),
(605, '强制删除', 'btn:student:delete', 6, 2, NULL, NULL, NULL, 5, 1),
(606, '查看学员日志', 'btn:student:view-log', 6, 2, NULL, NULL, NULL, 6, 1),
(607, '导出学员', 'btn:student:export', 6, 2, NULL, NULL, NULL, 7, 1);

-- 7. 礼品管理按钮权限
INSERT INTO sys_permission (id, permission_name, permission_code, parent_id, type, path, component, icon, sort, status) VALUES
(701, '查看礼品', 'btn:gift:view', 7, 2, NULL, NULL, NULL, 1, 1),
(702, '上架礼品', 'btn:gift:online', 7, 2, NULL, NULL, NULL, 2, 1),
(703, '下架礼品', 'btn:gift:offline', 7, 2, NULL, NULL, NULL, 3, 1),
(704, '修改库存', 'btn:gift:edit-stock', 7, 2, NULL, NULL, NULL, 4, 1),
(705, '删除礼品', 'btn:gift:delete', 7, 2, NULL, NULL, NULL, 5, 1),
(706, '导出礼品', 'btn:gift:export', 7, 2, NULL, NULL, NULL, 6, 1);

-- 8. 订单管理按钮权限
INSERT INTO sys_permission (id, permission_name, permission_code, parent_id, type, path, component, icon, sort, status) VALUES
(801, '查看订单', 'btn:order:view', 8, 2, NULL, NULL, NULL, 1, 1),
(802, '查看详情', 'btn:order:view-detail', 8, 2, NULL, NULL, NULL, 2, 1),
(803, '强制核销', 'btn:order:verify', 8, 2, NULL, NULL, NULL, 3, 1),
(804, '强制取消', 'btn:order:cancel', 8, 2, NULL, NULL, NULL, 4, 1),
(805, '导出订单', 'btn:order:export', 8, 2, NULL, NULL, NULL, 5, 1);

-- 9. 心愿便利贴管理按钮权限
INSERT INTO sys_permission (id, permission_name, permission_code, parent_id, type, path, component, icon, sort, status) VALUES
(901, '查看心愿', 'btn:wish:view', 9, 2, NULL, NULL, NULL, 1, 1),
(902, '查看发布人', 'btn:wish:view-publisher', 9, 2, NULL, NULL, NULL, 2, 1),
(903, '删除心愿', 'btn:wish:delete', 9, 2, NULL, NULL, NULL, 3, 1),
(904, '导出心愿', 'btn:wish:export', 9, 2, NULL, NULL, NULL, 4, 1);

-- 10. 意见征集管理按钮权限
INSERT INTO sys_permission (id, permission_name, permission_code, parent_id, type, path, component, icon, sort, status) VALUES
(1001, '查看帖子', 'btn:suggestion:view', 10, 2, NULL, NULL, NULL, 1, 1),
(1002, '删除帖子', 'btn:suggestion:delete-post', 10, 2, NULL, NULL, NULL, 2, 1),
(1003, '删除评论', 'btn:suggestion:delete-comment', 10, 2, NULL, NULL, NULL, 3, 1),
(1004, '导出意见', 'btn:suggestion:export', 10, 2, NULL, NULL, NULL, 4, 1);

-- 11. 系统日志按钮权限
INSERT INTO sys_permission (id, permission_name, permission_code, parent_id, type, path, component, icon, sort, status) VALUES
(1101, '查看日志', 'btn:log:view', 11, 2, NULL, NULL, NULL, 1, 1),
(1102, '查看详情', 'btn:log:view-detail', 11, 2, NULL, NULL, NULL, 2, 1),
(1103, '导出日志', 'btn:log:export', 11, 2, NULL, NULL, NULL, 3, 1);

-- 12. 系统设置按钮权限
INSERT INTO sys_permission (id, permission_name, permission_code, parent_id, type, path, component, icon, sort, status) VALUES
(1201, '查看设置', 'btn:settings:view', 12, 2, NULL, NULL, NULL, 1, 1),
(1202, '编辑设置', 'btn:settings:edit', 12, 2, NULL, NULL, NULL, 2, 1),
(1203, '清理缓存', 'btn:settings:clear-cache', 12, 2, NULL, NULL, NULL, 3, 1);

-- =============================================
-- 三、角色权限分配
-- =============================================

-- super_admin (role_id=1) 拥有所有权限
INSERT INTO sys_role_permission (role_id, permission_id)
SELECT 1, id FROM sys_permission;

-- admin (role_id=2) 权限分配
-- 可访问：控制台、用户、班级、学员、礼品、订单、心愿、意见、系统日志
-- 不可访问：角色管理、权限管理、系统设置
INSERT INTO sys_role_permission (role_id, permission_id)
SELECT 2, id FROM sys_permission WHERE id IN (
    -- 控制台
    1, 101,
    -- 用户管理
    2, 201, 202, 203, 204, 207,
    -- 班级管理
    5, 501, 502, 503, 504, 505, 507,
    -- 学员管理
    6, 601, 602, 603, 604, 605, 606, 607,
    -- 礼品管理
    7, 701, 702, 703, 704, 705, 706,
    -- 订单管理
    8, 801, 802, 803, 804, 805,
    -- 心愿便利贴管理
    9, 901, 902, 903, 904,
    -- 意见征集管理
    10, 1001, 1002, 1003, 1004,
    -- 系统日志
    11, 1101, 1102, 1103
);

-- teacher (role_id=3) 和 student (role_id=4) 不能进入后台，不分配任何后台权限
