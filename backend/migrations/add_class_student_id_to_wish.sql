-- 添加 class_student_id 字段到心愿表
ALTER TABLE wish 
ADD COLUMN class_student_id INT NULL COMMENT '班级学员ID（关联到具体的学员绑定记录）';

-- 添加外键约束
ALTER TABLE wish 
ADD CONSTRAINT fk_wish_class_student 
FOREIGN KEY (class_student_id) REFERENCES class_student(id);

-- 添加索引
CREATE INDEX idx_wish_class_student_id ON wish(class_student_id);