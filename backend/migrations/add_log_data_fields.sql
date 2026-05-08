-- 为系统日志表添加 before_data 和 after_data 字段
ALTER TABLE system_log ADD COLUMN before_data TEXT COMMENT '操作前数据';
ALTER TABLE system_log ADD COLUMN after_data TEXT COMMENT '操作后数据';
