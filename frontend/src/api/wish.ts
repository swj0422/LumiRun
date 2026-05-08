import request from './request';

export const wishApi = {
  getWishList: (params: Record<string, any>): Promise<{ items: any[]; total: number }> => {
    return request.get('/api/v1/wishes', { params }) as Promise<{ items: any[]; total: number }>;
  },
  
  createWish: (data: FormData): Promise<any> => {
    return request.post('/api/v1/wishes', data) as Promise<any>;
  },
  
  deleteWish: (wishId: number): Promise<{ message: string }> => {
    return request.delete(`/api/v1/wishes/${wishId}`) as Promise<{ message: string }>;
  },
  
  adminDeleteWish: (wishId: number): Promise<{ message: string }> => {
    return request.delete(`/api/v1/wishes/admin/${wishId}`) as Promise<{ message: string }>;
  },
};