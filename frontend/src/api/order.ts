import request from './request';

// 获取订单列表
export const getOrders = (params?: {
  class_id?: number;
  status?: number;
  skip?: number;
  limit?: number;
}) => {
  return request.get('/v1/orders/', { params });
};

// 获取导师的订单列表（兼容旧路径）
export const getTeacherOrders = (params?: {
  class_id?: number;
  status?: number;
  skip?: number;
  limit?: number;
}) => {
  return request.get('/v1/orders/teacher', { params });
};

// 获取学员的订单列表
export const getUserOrders = (params?: {
  status?: number;
  skip?: number;
  limit?: number;
}) => {
  return request.get('/v1/orders/user', { params });
};

// 审核通过订单
export const approveOrder = (orderId: number) => {
  return request.post(`/v1/orders/${orderId}/approve`);
};

// 拒绝订单
export const rejectOrder = (orderId: number, reason: string) => {
  return request.post(`/v1/orders/${orderId}/reject`, { reason });
};

// 创建兑换订单
export const createOrder = (data: { gift_id: number; class_id: number }) => {
  return request.post('/v1/orders/', data);
};

// 导师为学生兑换奖励
export const createTeacherOrder = (data: {
  gift_id: number;
  class_id: number;
  user_id: number;
  quantity?: number;
}) => {
  return request.post('/v1/orders/teacher', data);
};
