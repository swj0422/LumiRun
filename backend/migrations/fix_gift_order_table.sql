-- 修复 gift_order 表结构，使其与 GiftOrder 模型匹配

USE lumirun;

-- 重命名旧表，以防止数据丢失
RENAME TABLE gift_order TO gift_order_old;

-- 创建新的 gift_order 表，与 GiftOrder 模型匹配
CREATE TABLE IF NOT EXISTS gift_order (
    id INT AUTO_INCREMENT PRIMARY KEY,
    class_student_id INT NOT NULL COMMENT '学员ID',
    gift_id INT NOT NULL COMMENT '礼品ID',
    class_id INT NOT NULL COMMENT '班级ID',
    teacher_id INT NOT NULL COMMENT '导师ID',
    creator_id INT COMMENT '创建人ID（发起兑换的用户ID）',
    operator_id INT COMMENT '当前操作人ID',
    price INT NOT NULL COMMENT '兑换消耗的成长值',
    status INT DEFAULT 0 COMMENT '订单状态：0-待审核，1-待核销，2-已完成，3-已取消',
    qr_code VARCHAR(64) UNIQUE NOT NULL COMMENT '订单核销二维码唯一标识',
    cancel_reason VARCHAR(255) COMMENT '取消原因',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '订单创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '订单状态更新时间',
    FOREIGN KEY (class_student_id) REFERENCES class_student(id),
    FOREIGN KEY (gift_id) REFERENCES gift(id),
    FOREIGN KEY (class_id) REFERENCES class_info(id),
    FOREIGN KEY (teacher_id) REFERENCES sys_user(id),
    FOREIGN KEY (creator_id) REFERENCES sys_user(id),
    FOREIGN KEY (operator_id) REFERENCES sys_user(id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 如果旧表存在，尝试迁移数据
-- 注意：这里需要根据实际情况调整迁移逻辑
-- 由于表结构变化较大，可能需要手动处理数据迁移

-- 检查旧表是否存在
IF EXISTS (SELECT * FROM information_schema.tables WHERE table_schema = 'lumirun' AND table_name = 'gift_order_old') THEN
    -- 这里可以添加数据迁移逻辑
    -- 例如：
    -- INSERT INTO gift_order (id, class_student_id, gift_id, class_id, teacher_id, creator_id, operator_id, price, status, qr_code, cancel_reason, created_at, updated_at)
    -- SELECT id, user_id, gift_id, class_id, (SELECT teacher_id FROM class_info WHERE id = class_id), user_id, NULL, total_price, status, qr_code, reject_reason, order_time, order_time
    -- FROM gift_order_old;
    
    -- 注意：上面的迁移逻辑只是示例，实际需要根据数据库中的实际数据结构进行调整
    -- 特别是 class_student_id 需要根据 user_id 和 class_id 来查找对应的 class_student 记录
    
    -- 迁移完成后，可以删除旧表
    -- DROP TABLE gift_order_old;
END IF;

-- 提示信息
SELECT 'gift_order 表结构修复完成' AS message;