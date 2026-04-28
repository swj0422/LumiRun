import request from './request';

// 获取礼品列表
export const getGifts = (params?: {
  class_id?: number;
  status?: number;
  skip?: number;
  limit?: number;
}) => {
  return request.get('/v1/gifts/', { params });
};

// 获取礼品详情
export const getGiftDetail = (giftId: number) => {
  return request.get(`/v1/gifts/${giftId}`);
};

// 创建礼品
export const createGift = (data: {
  name: string;
  description: string;
  price: number;
  image: string;
  status: number;
  class_ids: number[];
}) => {
  return request.post('/v1/gifts/', data);
};

// 更新礼品
export const updateGift = (
  giftId: number,
  data: {
    name?: string;
    description?: string;
    price?: number;
    image?: string;
    status?: number;
    class_ids?: number[];
  }
) => {
  return request.put(`/v1/gifts/${giftId}`, data);
};

// 删除礼品
export const deleteGift = (giftId: number) => {
  return request.delete(`/v1/gifts/${giftId}`);
};

// 获取礼品库存
export const getGiftStock = (giftId: number) => {
  return request.get(`/v1/gifts/stock/${giftId}`);
};

// 批量更新礼品库存
export const batchUpdateStock = (
  data: {
    gift_id: number;
    quantity: number;
    type: string;
    reason: string;
  }[]
) => {
  return request.post('/v1/gifts/stock/batch', data);
};
