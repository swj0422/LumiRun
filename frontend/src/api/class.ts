import request from './request';

// 获取组织列表
export const getClasses = (params?: {
  status?: number;
  skip?: number;
  limit?: number;
}) => {
  return request.get('/api/v1/classes/', { params });
};

// 获取组织助理列表
export const getClassAssistants = (classId: number) => {
  return request.get(`/api/v1/class-assistants/class/${classId}`);
};

// 添加组织助理
export const addClassAssistant = (data: {
  class_id: number;
  assistant_id: number;
  assistant_email: string;
}) => {
  return request.post('/api/v1/class-assistants', data);
};

// 移除组织助理
export const removeClassAssistant = (classId: number, assistantId: number) => {
  return request.delete('/api/v1/class-assistants', {
    data: {
      class_id: classId,
      assistant_id: assistantId
    }
  });
};

// 获取用户作为助理的组织列表
export const getUserAssistantClasses = () => {
  return request.get('/api/v1/class-assistants/user');
};

// 检查用户是否有组织助理授权记录
export const checkUserAssistantStatus = () => {
  return request.get('/api/v1/class-assistants/user/check');
};

// 获取组织详情
export const getClassDetail = (classId: number) => {
  return request.get(`/api/v1/classes/${classId}`);
};

// 创建组织
export const createClass = (data: {
  class_name: string;
  school_name: string;
  session: string;
  status: number;
}) => {
  return request.post('/api/v1/classes/', data);
};

// 更新组织
export const updateClass = (
  classId: number,
  data: {
    class_name?: string;
    school_name?: string;
    session?: string;
    status?: number;
  }
) => {
  return request.put(`/api/v1/classes/${classId}`, data);
};

// 删除组织
export const deleteClass = (classId: number) => {
  return request.delete(`/api/v1/classes/${classId}`);
};

// 批量导入组织成员
export const batchImportStudents = (
  classId: number,
  data: {
    students: {
      name_in_class: string;
      student_no_in_class: string;
    }[];
  }
) => {
  return request.post(`/api/v1/classes/${classId}/students/import`, data);
};

// 获取组织二维码
export const getClassQRCode = (classId: number) => {
  return request.get(`/api/v1/classes/${classId}/qrcode`);
};

// 审核成员绑定
export const auditStudentBind = (
  classId: number,
  studentClassId: number,
  status: string,
  reason?: string
) => {
  return request.post(
    `/api/v1/classes/${classId}/students/${studentClassId}/audit`,
    { status, reason }
  );
};

// 获取组织成员列表
export const getClassStudents = (classId: number) => {
  return request.get(`/api/v1/classes/${classId}/students`);
};
