-- 添加 class_student_id 字段到 growth_log 表
ALTER TABLE growth_log ADD COLUMN class_student_id INT NULL COMMENT '班级学员ID（导师直接导入的学员）';
ALTER TABLE growth_log ADD CONSTRAINT fk_growth_log_class_student FOREIGN KEY (class_student_id) REFERENCES class_student(id);
