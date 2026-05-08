-- 创建心愿便利贴表
CREATE TABLE IF NOT EXISTS wish (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
    user_id INT NOT NULL COMMENT '发布人ID',
    class_student_id INT NULL COMMENT '学员ID（可选）',
    content VARCHAR(200) NOT NULL COMMENT '心愿文字内容（1-200字）',
    image_url VARCHAR(255) NULL COMMENT '图片地址',
    is_anonymous TINYINT(1) DEFAULT 0 NOT NULL COMMENT '是否匿名：1-匿名，0-不匿名',
    is_deleted TINYINT(1) DEFAULT 0 NOT NULL COMMENT '是否已删除：0-正常，1-已删除',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL COMMENT '发布时间',
    INDEX idx_wish_user_id (user_id),
    INDEX idx_wish_class_student_id (class_student_id),
    INDEX idx_wish_created_at (created_at),
    FOREIGN KEY (user_id) REFERENCES sys_user(id),
    FOREIGN KEY (class_student_id) REFERENCES class_student(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='心愿便利贴表';