import request from './request';

// 记录成长值变动
export const recordGrowth = (data: {
  student_name: string;
  change_score: number;
  reason: string;
  input_type: number;
}) => {
  return request.post('/v1/growth/record', data);
};

// 获取成长值流水
export const getGrowthLogs = (params?: {
  class_id?: number;
  student_name?: string;
  school_name?: string;
  session?: string;
  class_name?: string;
  start_time?: string;
  end_time?: string;
  change_type?: string;
  skip?: number;
  limit?: number;
}) => {
  return request.get('/v1/growth/logs', { params });
};

// 获取成长值总额
export const getGrowthScore = () => {
  return request.get('/v1/growth/score');
};

// 删除成长值记录
export const deleteGrowthLog = (logId: number) => {
  return request.delete(`/v1/growth/logs/${logId}`);
};

// 获取成长值变更流水（所有操作，包括添加和删除）
export const getGrowthHistory = (params?: {
  start_time?: string;
  end_time?: string;
  skip?: number;
  limit?: number;
}) => {
  return request.get('/v1/growth/history', { params });
};
