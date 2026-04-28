-- 修改 growth_log 表，让 user_id 字段可以为空
ALTER TABLE growth_log MODIFY COLUMN user_id INT(11) NULL;

-- 修改 growth_score 表，添加 student_class_id 字段，并让 user_id 字段可以为空
ALTER TABLE growth_score MODIFY COLUMN user_id INT(11) NULL;
ALTER TABLE growth_score ADD COLUMN student_class_id INT(11) NULL AFTER user_id;
ALTER TABLE growth_score ADD CONSTRAINT growth_score_ibfk_2 FOREIGN KEY (student_class_id) REFERENCES student_class(id);
ALTER TABLE growth_score ADD UNIQUE KEY uk_student_class_id (student_class_id);
