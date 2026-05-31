import request from './request';

// 获取管理者的成员列表
export const getTeacherStudents = (params?: {
  class_id?: number;
  keyword?: string;
  status?: string;
  sort?: string;
  order?: string;
  school_name?: string;
}) => {
  return request.get('/v1/students/teacher-students', { params });
};

// 获取组织成员列表
export const getClassStudents = (classId: number) => {
  return request.get(`/v1/students/class-students/${classId}`);
};

// 搜索成员
export const searchStudents = (keyword: string) => {
  return request.get('/v1/students/search', { params: { keyword } });
};

// 获取成员备注
export const getStudentNote = (classStudentId: number) => {
  return request.get(`/v1/students/note/${classStudentId}`);
};

// 创建或更新成员备注
export const updateStudentNote = (
  classStudentId: number,
  data: {
    learning_characteristics?: string;
    personality_suggestions?: string;
    performance_summary?: string;
  }
) => {
  return request.post(`/v1/students/note/${classStudentId}`, data);
};

// 获取成员标签
export const getStudentTags = (classStudentId: number) => {
  return request.get(`/v1/students/tags/${classStudentId}`);
};

// 更新成员标签
export const updateStudentTags = (classStudentId: number, tagIds: number[]) => {
  return request.post(`/v1/students/tags/${classStudentId}`, {
    tag_ids: tagIds,
  });
};

// 停用成员
export const stopStudent = (studentClassId: number) => {
  return request.post(`/v1/students/stop/${studentClassId}`);
};

// 解绑成员
export const removeStudent = (studentClassId: number, reason: string) => {
  return request.post(`/v1/students/remove/${studentClassId}`, { reason });
};

// 成员绑定组织
export const bindClass = (data: {
  qr_code: string;
  real_name: string;
  phone: string;
}) => {
  return request.post('/v1/students/bind', data);
};

// 获取我的绑定组织
export const getMyClasses = () => {
  return request.get('/v1/students/my-classes');
};
