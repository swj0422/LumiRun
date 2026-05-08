-- 创建 system_log 表
USE lumirun;

CREATE TABLE IF NOT EXISTS system_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT COMMENT '操作用户ID',
    username VARCHAR(50) COMMENT '操作用户名',
    real_name VARCHAR(50) COMMENT '操作用户真实姓名',
    log_type VARCHAR(20) COMMENT '日志类型',
    log_level VARCHAR(20) DEFAULT 'info' COMMENT '日志级别',
    module VARCHAR(100) COMMENT '操作模块',
    action VARCHAR(100) COMMENT '操作动作',
    biz_type VARCHAR(50) COMMENT '业务类型',
    biz_id INT COMMENT '业务ID',
    ip_address VARCHAR(50) COMMENT '操作IP地址',
    user_agent VARCHAR(500) COMMENT '用户代理',
    request_url VARCHAR(500) COMMENT '请求URL',
    request_method VARCHAR(10) COMMENT '请求方法',
    request_params TEXT COMMENT '请求参数',
    response_status INT COMMENT '响应状态码',
    error_message TEXT COMMENT '错误信息',
    before_data TEXT COMMENT '操作前数据',
    after_data TEXT COMMENT '操作后数据',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '日志创建时间',
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at),
    INDEX idx_log_type (log_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
