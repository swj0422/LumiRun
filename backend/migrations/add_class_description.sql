-- 添加班级描述字段
USE lumirun;

ALTER TABLE class_info ADD COLUMN description VARCHAR(500) NULL COMMENT '班级描述' AFTER class_name;

-- 验证
DESCRIBE class_info;
