-- 逐光成长系统数据库初始化脚本
-- 简化版本

-- 删除旧数据库（如果存在）
DROP DATABASE IF EXISTS lumirun;

-- 创建数据库，指定字符集
CREATE DATABASE lumirun CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE lumirun;

-- 角色表
CREATE TABLE sys_role (
    id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL UNIQUE,
    remark VARCHAR(255)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 插入角色数据
INSERT INTO sys_role (id, role_name, remark) VALUES
(1, '超级管理员', '系统最高权限，可管理所有功能'),
(2, '管理员', '管理用户和日志，不可操作业务数据'),
(3, '导师', '管理班级、学员、成长值、奖励'),
(4, '学员', '查看成长值、兑换奖励');

-- 用户表
CREATE TABLE sys_user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    real_name VARCHAR(50) NOT NULL,
    phone VARCHAR(20),
    role_id INT NOT NULL,
    status TINYINT(1) DEFAULT 1,
    last_login_time DATETIME,
    login_count INT DEFAULT 0,
    login_error_count INT DEFAULT 0,
    locked_until DATETIME,
    password_reset_token VARCHAR(100),
    password_reset_expires DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES sys_role(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建超级管理员账号
-- 邮箱: admin@example.com, 密码: Password123 (pbkdf2_sha256加密)
INSERT INTO sys_user (id, email, password, real_name, phone, role_id, status, login_count) VALUES
(1, 'admin@example.com', '$pbkdf2-sha256$29000$da4VgtAaY8y5dy7F2Pt/Dw$n2.jin76GFP4WyRdpMt7BaedMzNM/Ge5MF/bWEVSBxY', '超级管理员', '13800138000', 1, 1, 0);

-- 验证数据
SELECT id, role_name FROM sys_role;
SELECT id, email, real_name, role_id FROM sys_user;