-- 逐光成长系统数据库初始化脚本
-- MySQL 5.6 兼容版本

-- 创建数据库
CREATE DATABASE IF NOT EXISTS lumirun CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE lumirun;

-- 角色表
CREATE TABLE IF NOT EXISTS sys_role (
    id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL UNIQUE COMMENT '角色名称',
    remark VARCHAR(255) COMMENT '角色说明'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 用户表
CREATE TABLE IF NOT EXISTS sys_user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) NOT NULL UNIQUE COMMENT '邮箱（登录账号）',
    password VARCHAR(255) NOT NULL COMMENT '密码（加密存储）',
    real_name VARCHAR(50) NOT NULL COMMENT '真实姓名',
    phone VARCHAR(20) COMMENT '手机号（选填）',
    role_id INT NOT NULL COMMENT '角色ID',
    status TINYINT(1) DEFAULT 1 COMMENT '账号状态：0-禁用，1-启用',
    last_login_time DATETIME COMMENT '最后登录时间',
    login_count INT DEFAULT 0 COMMENT '登录次数',
    login_error_count INT DEFAULT 0 COMMENT '连续登录错误次数',
    locked_until DATETIME COMMENT '账号锁定截止时间',
    password_reset_token VARCHAR(100) COMMENT '密码重置令牌',
    password_reset_expires DATETIME COMMENT '密码重置令牌过期时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '账号创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '账号更新时间',
    FOREIGN KEY (role_id) REFERENCES sys_role(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 班级表
CREATE TABLE IF NOT EXISTS class_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    school_name VARCHAR(100) NOT NULL COMMENT '学校名称',
    session VARCHAR(20) NOT NULL COMMENT '届别',
    class_name VARCHAR(50) NOT NULL COMMENT '班级名称',
    teacher_id INT NOT NULL COMMENT '创建导师ID',
    status TINYINT(1) DEFAULT 1 COMMENT '班级状态：0-关闭，1-开放',
    qr_code VARCHAR(100) NOT NULL UNIQUE COMMENT '班级绑定二维码唯一标识',
    qr_url VARCHAR(255) COMMENT '班级绑定二维码图片地址',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '班级创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '班级更新时间',
    FOREIGN KEY (teacher_id) REFERENCES sys_user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 学员班级绑定表
CREATE TABLE IF NOT EXISTS student_class (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '学员ID',
    class_id INT NOT NULL COMMENT '班级ID',
    status TINYINT(1) DEFAULT 1 COMMENT '绑定状态：0-解绑，1-绑定',
    bind_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '绑定时间',
    unbind_time DATETIME COMMENT '解绑时间',
    FOREIGN KEY (user_id) REFERENCES sys_user(id),
    FOREIGN KEY (class_id) REFERENCES class_info(id),
    UNIQUE KEY uk_user_class (user_id, class_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 成长值总表
CREATE TABLE IF NOT EXISTS growth_score (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE COMMENT '学员ID',
    total_score INT DEFAULT 0 COMMENT '累计成长值（只增不减）',
    available_score INT DEFAULT 0 COMMENT '可用成长值（可增可减，可为负）',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '成长值更新时间',
    FOREIGN KEY (user_id) REFERENCES sys_user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 成长值变动记录表
CREATE TABLE IF NOT EXISTS growth_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '学员ID',
    class_id INT COMMENT '班级ID',
    change_score INT NOT NULL COMMENT '成长值变动（正数增加，负数减少）',
    reason VARCHAR(100) COMMENT '变动原因',
    teacher_id INT COMMENT '操作导师ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '变动时间',
    FOREIGN KEY (user_id) REFERENCES sys_user(id),
    FOREIGN KEY (class_id) REFERENCES class_info(id),
    FOREIGN KEY (teacher_id) REFERENCES sys_user(id),
    INDEX idx_user_id (user_id),
    INDEX idx_class_id (class_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 成长原因表
CREATE TABLE IF NOT EXISTS growth_reason (
    id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id INT NOT NULL COMMENT '导师ID',
    reason VARCHAR(100) NOT NULL COMMENT '原因名称',
    default_score INT DEFAULT 5 COMMENT '默认分值',
    status TINYINT(1) DEFAULT 1 COMMENT '状态：0-禁用，1-启用',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (teacher_id) REFERENCES sys_user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 礼品表
CREATE TABLE IF NOT EXISTS gift (
    id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id INT NOT NULL COMMENT '导师ID',
    name VARCHAR(100) NOT NULL COMMENT '礼品名称',
    description VARCHAR(500) COMMENT '礼品描述',
    price INT NOT NULL COMMENT '礼品价格',
    stock INT DEFAULT 0 COMMENT '礼品库存',
    image_path VARCHAR(255) COMMENT '礼品图片路径',
    status TINYINT(1) DEFAULT 1 COMMENT '状态：0-下架，1-上架',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (teacher_id) REFERENCES sys_user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 礼品班级开放范围表
CREATE TABLE IF NOT EXISTS gift_class_relation (
    id INT AUTO_INCREMENT PRIMARY KEY,
    gift_id INT NOT NULL COMMENT '礼品ID',
    class_id INT NOT NULL COMMENT '班级ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (gift_id) REFERENCES gift(id),
    FOREIGN KEY (class_id) REFERENCES class_info(id),
    UNIQUE KEY uk_gift_class (gift_id, class_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 礼品库存变动记录表
CREATE TABLE IF NOT EXISTS gift_stock (
    id INT AUTO_INCREMENT PRIMARY KEY,
    gift_id INT NOT NULL COMMENT '礼品ID',
    change_quantity INT NOT NULL COMMENT '变动数量',
    reason VARCHAR(100) COMMENT '变动原因',
    operator_id INT COMMENT '操作人ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '变动时间',
    FOREIGN KEY (gift_id) REFERENCES gift(id),
    FOREIGN KEY (operator_id) REFERENCES sys_user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 礼品订单表
CREATE TABLE IF NOT EXISTS gift_order (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '学员ID',
    gift_id INT NOT NULL COMMENT '礼品ID',
    class_id INT NOT NULL COMMENT '班级ID',
    quantity INT DEFAULT 1 COMMENT '兑换数量',
    total_price INT NOT NULL COMMENT '总消耗积分',
    status TINYINT(1) DEFAULT 0 COMMENT '状态：0-待审核，1-已确认，2-已发货，3-已拒绝，4-已完成',
    reject_reason VARCHAR(200) COMMENT '拒绝原因',
    qr_code VARCHAR(100) COMMENT '兑换二维码',
    order_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '下单时间',
    confirm_time DATETIME COMMENT '确认时间',
    delivery_time DATETIME COMMENT '发货时间',
    complete_time DATETIME COMMENT '完成时间',
    FOREIGN KEY (user_id) REFERENCES sys_user(id),
    FOREIGN KEY (gift_id) REFERENCES gift(id),
    FOREIGN KEY (class_id) REFERENCES class_info(id),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_order_time (order_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 学员心愿单表
CREATE TABLE IF NOT EXISTS user_wish (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '学员ID',
    gift_id INT NOT NULL COMMENT '礼品ID',
    status TINYINT(1) DEFAULT 0 COMMENT '状态：0-未通知，1-已通知',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    notify_time DATETIME COMMENT '通知时间',
    FOREIGN KEY (user_id) REFERENCES sys_user(id),
    FOREIGN KEY (gift_id) REFERENCES gift(id),
    UNIQUE KEY uk_user_gift (user_id, gift_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 消息通知表
CREATE TABLE IF NOT EXISTS message (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '用户ID',
    content VARCHAR(500) NOT NULL COMMENT '消息内容',
    type TINYINT(1) NOT NULL DEFAULT 0 COMMENT '消息类型：0-系统通知，1-解绑通知，2-礼品补货通知，3-成长值变动通知，4-订单状态通知',
    is_read TINYINT(1) DEFAULT 0 COMMENT '是否已读：0-未读，1-已读',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (user_id) REFERENCES sys_user(id),
    INDEX idx_user_id (user_id),
    INDEX idx_is_read (is_read),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 礼品核销记录表
CREATE TABLE IF NOT EXISTS verify_record (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL COMMENT '订单ID',
    class_id INT NOT NULL COMMENT '班级ID',
    operator_id INT NOT NULL COMMENT '核销人ID',
    verify_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '核销时间',
    remark VARCHAR(200) COMMENT '备注',
    FOREIGN KEY (order_id) REFERENCES gift_order(id),
    FOREIGN KEY (class_id) REFERENCES class_info(id),
    FOREIGN KEY (operator_id) REFERENCES sys_user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 系统日志表
CREATE TABLE IF NOT EXISTS sys_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT COMMENT '操作用户ID',
    username VARCHAR(50) COMMENT '操作用户名',
    operation VARCHAR(100) COMMENT '操作描述',
    method VARCHAR(10) COMMENT '请求方法',
    path VARCHAR(255) COMMENT '请求路径',
    ip VARCHAR(50) COMMENT 'IP地址',
    params TEXT COMMENT '请求参数',
    result TEXT COMMENT '返回结果',
    status_code INT COMMENT '状态码',
    cost_time INT COMMENT '耗时（毫秒）',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 初始化角色数据
INSERT INTO sys_role (id, role_name, remark) VALUES
(1, '超级管理员', '系统最高权限，可管理所有功能'),
(2, '管理员', '管理用户和日志，不可操作业务数据'),
(3, '导师', '管理班级、学员、成长值、奖励'),
(4, '学员', '查看成长值、兑换奖励')
ON DUPLICATE KEY UPDATE role_name = VALUES(role_name);

-- 创建超级管理员账号
-- 邮箱: admin@example.com, 密码: Password123 (pbkdf2_sha256加密)
INSERT INTO sys_user (id, email, password, real_name, phone, role_id, status, login_count) VALUES
(1, 'admin@example.com', '$pbkdf2-sha256$29000$da4VgtAaY8y5dy7F2Pt/Dw$n2.jin76GFP4WyRdpMt7BaedMzNM/Ge5MF/bWEVSBxY', '超级管理员', '13800138000', 1, 1, 0)
ON DUPLICATE KEY UPDATE email = VALUES(email);

-- 创建测试管理者账号
-- 邮箱: manager@example.com, 密码: Password123 (pbkdf2_sha256加密)
INSERT INTO sys_user (id, email, password, real_name, phone, role_id, status, login_count) VALUES
(2, 'manager@example.com', '$pbkdf2-sha256$29000$da4VgtAaY8y5dy7F2Pt/Dw$n2.jin76GFP4WyRdpMt7BaedMzNM/Ge5MF/bWEVSBxY', '张管理者', '13800138001', 3, 1, 0)
ON DUPLICATE KEY UPDATE email = VALUES(email);

-- 创建测试成员账号
-- 邮箱: member@example.com, 密码: Password123 (pbkdf2_sha256加密)
INSERT INTO sys_user (id, email, password, real_name, phone, role_id, status, login_count) VALUES
(3, 'member@example.com', '$pbkdf2-sha256$29000$da4VgtAaY8y5dy7F2Pt/Dw$n2.jin76GFP4WyRdpMt7BaedMzNM/Ge5MF/bWEVSBxY', '李成员', '13800138002', 4, 1, 0)
ON DUPLICATE KEY UPDATE email = VALUES(email);

-- 创建测试班级
INSERT INTO class_info (id, school_name, session, class_name, teacher_id, status, qr_code) VALUES
(1, '测试学校', '2024', '高一(1)班', 2, 1, 'class_001')
ON DUPLICATE KEY UPDATE qr_code = VALUES(qr_code);

-- 创建学员成长值记录
INSERT INTO growth_score (id, user_id, total_score, available_score) VALUES
(1, 3, 100, 100)
ON DUPLICATE KEY UPDATE total_score = VALUES(total_score);

-- 初始化成长原因
INSERT INTO growth_reason (teacher_id, reason, default_score, status) VALUES
(2, '按时完成作业', 5, 1),
(2, '课堂积极发言', 3, 1),
(2, '帮助同学', 5, 1),
(2, '考试成绩优秀', 10, 1),
(2, '参与活动', 5, 1)
ON DUPLICATE KEY UPDATE reason = VALUES(reason);
