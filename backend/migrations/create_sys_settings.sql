-- 创建系统设置表
CREATE TABLE IF NOT EXISTS sys_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    setting_key VARCHAR(100) NOT NULL UNIQUE COMMENT '设置键',
    setting_value TEXT COMMENT '设置值',
    setting_type VARCHAR(50) DEFAULT 'string' COMMENT '设置类型：string/number/boolean/json',
    category VARCHAR(50) DEFAULT 'general' COMMENT '设置分类：general/security/upload/email/feature',
    description VARCHAR(255) COMMENT '设置描述',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统设置表';

-- 初始化系统设置数据
-- 基础设置
INSERT INTO sys_settings (setting_key, setting_value, setting_type, category, description) VALUES
('site_name', '逐光成长系统', 'string', 'general', '系统名称'),
('site_description', '学员成长记录管理系统', 'string', 'general', '系统描述'),
('contact_email', '', 'string', 'general', '联系邮箱'),
('contact_phone', '', 'string', 'general', '联系电话');

-- 安全设置
INSERT INTO sys_settings (setting_key, setting_value, setting_type, category, description) VALUES
('login_error_limit', '5', 'number', 'security', '登录错误次数限制'),
('login_lock_time', '30', 'number', 'security', '账号锁定时间（分钟）'),
('password_min_length', '6', 'number', 'security', '密码最小长度'),
('password_require_special', 'false', 'boolean', 'security', '密码是否需要特殊字符'),
('session_timeout', '1440', 'number', 'security', '会话超时时间（分钟）');

-- 上传设置
INSERT INTO sys_settings (setting_key, setting_value, setting_type, category, description) VALUES
('upload_max_size', '10', 'number', 'upload', '文件上传最大大小（MB）'),
('upload_allowed_types', 'jpg,jpeg,png,gif,pdf,doc,docx,xls,xlsx', 'string', 'upload', '允许上传的文件类型'),
('upload_image_max_size', '5', 'number', 'upload', '图片上传最大大小（MB）'),
('upload_image_types', 'jpg,jpeg,png,gif', 'string', 'upload', '允许上传的图片类型');

-- 功能开关
INSERT INTO sys_settings (setting_key, setting_value, setting_type, category, description) VALUES
('feature_wish_wall', 'true', 'boolean', 'feature', '心愿墙功能开关'),
('feature_suggestion', 'true', 'boolean', 'feature', '意见征集功能开关'),
('feature_register', 'true', 'boolean', 'feature', '注册功能开关'),
('feature_gift_exchange', 'true', 'boolean', 'feature', '礼品兑换功能开关');

-- 邮箱设置
INSERT INTO sys_settings (setting_key, setting_value, setting_type, category, description) VALUES
('smtp_host', '', 'string', 'email', 'SMTP服务器地址'),
('smtp_port', '465', 'number', 'email', 'SMTP端口'),
('smtp_user', '', 'string', 'email', 'SMTP用户名'),
('smtp_password', '', 'string', 'email', 'SMTP密码'),
('smtp_from_email', '', 'string', 'email', '发件人邮箱'),
('smtp_from_name', '逐光成长系统', 'string', 'email', '发件人名称'),
('smtp_use_ssl', 'true', 'boolean', 'email', '是否使用SSL');
