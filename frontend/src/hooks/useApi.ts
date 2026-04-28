import { ref, reactive } from 'vue';
import request from '@/api/request';

interface ApiOptions {
  immediate?: boolean;
  onSuccess?: (data: any) => void;
  onError?: (error: any) => void;
}

export function useApi<T = any>(url: string, options: ApiOptions = {}) {
  const { immediate = false, onSuccess, onError } = options;

  const data = ref<T | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const execute = async (params?: any, config?: any) => {
    loading.value = true;
    error.value = null;

    try {
      const response = await request.get<T>(url, { params, ...config });
      data.value = response;
      onSuccess?.(response);
      return response;
    } catch (err: any) {
      error.value = err.message || '请求失败';
      onError?.(err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const post = async (data: any, config?: any) => {
    loading.value = true;
    error.value = null;

    try {
      const response = await request.post<T>(url, data, config);
      data.value = response;
      onSuccess?.(response);
      return response;
    } catch (err: any) {
      error.value = err.message || '请求失败';
      onError?.(err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const put = async (data: any, config?: any) => {
    loading.value = true;
    error.value = null;

    try {
      const response = await request.put<T>(url, data, config);
      data.value = response;
      onSuccess?.(response);
      return response;
    } catch (err: any) {
      error.value = err.message || '请求失败';
      onError?.(err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const del = async (config?: any) => {
    loading.value = true;
    error.value = null;

    try {
      const response = await request.delete<T>(url, config);
      data.value = response;
      onSuccess?.(response);
      return response;
    } catch (err: any) {
      error.value = err.message || '请求失败';
      onError?.(err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  // 立即执行
  if (immediate) {
    execute();
  }

  return {
    data,
    loading,
    error,
    execute,
    post,
    put,
    delete: del,
  };
}
