import axios, { type AxiosRequestConfig, type AxiosResponse } from 'axios';
import { getTokenFromCookie } from '@/utils/auth';

// 存储正在进行的请求
const pendingRequests = new Map<string, Promise<any>>();

// 生成请求唯一键的函数
function generateRequestKey(config: AxiosRequestConfig): string {
  const { url, method, params, data } = config;
  return `${method || 'get'}-${url}-${JSON.stringify(params || {})}-${JSON.stringify(data || {})}`;
}

// 自定义请求实例类型
type RequestInstance = {
  get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T>;
  post<T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<T>;
  put<T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<T>;
  delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T>;
  interceptors: {
    request: {
      use: (
        onFulfilled: (
          config: AxiosRequestConfig
        ) => AxiosRequestConfig | Promise<AxiosRequestConfig>,
        onRejected?: (error: any) => any
      ) => number;
    };
    response: {
      use: (
        onFulfilled: (response: AxiosResponse) => any,
        onRejected?: (error: any) => any
      ) => number;
    };
  };
};

// 创建axios实例
const axiosInstance = axios.create({
  baseURL: '',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// 请求拦截器
axiosInstance.interceptors.request.use(
  (config) => {
    const isLoginRequest = config.url?.includes('/auth/login');
    
    if (config.data instanceof FormData) {
      if (config.headers) {
        delete config.headers['Content-Type'];
      }
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
axiosInstance.interceptors.response.use(
  (response: AxiosResponse) => {
    if (response.data && typeof response.data === 'object') {
      return response.data;
    }
    return response.data as any;
  },
  (error) => {
    const { response, message } = error;

    if (response) {
      switch (response.status) {
        case 401:
          console.error('未授权，请重新登录');
          break;
        case 403:
          console.error('权限不足');
          break;
        case 404:
          console.error('请求的资源不存在');
          break;
        case 500:
          console.error('服务器错误');
          break;
        default:
          console.error(
            response.data?.detail || response.data?.msg || '请求失败'
          );
      }
    } else {
      console.error('网络错误:', message || '未知网络错误');
    }

    const errorMessage =
      response?.data?.detail || response?.data?.msg || message || '请求失败';
    const errorObj = {
      ...error,
      message: errorMessage,
      status: response?.status,
    };

    return Promise.reject(errorObj);
  }
);

// 包装axios实例，添加合并重复请求的功能
const request = {
  get: <T = any>(url: string, config?: AxiosRequestConfig): Promise<T> => {
    const requestConfig = { ...config, url, method: 'get' };
    const requestKey = generateRequestKey(requestConfig);

    if (pendingRequests.has(requestKey)) {
      return pendingRequests.get(requestKey) as Promise<T>;
    }

    const requestPromise = axiosInstance.get<T>(url, config).then(data => {
      return data as T;
    }).finally(() => {
      pendingRequests.delete(requestKey);
    });

    pendingRequests.set(requestKey, requestPromise);

    return requestPromise;
  },
  post: <T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<T> => {
    const requestConfig = { ...config, url, method: 'post', data };
    const requestKey = generateRequestKey(requestConfig);

    if (pendingRequests.has(requestKey)) {
      return pendingRequests.get(requestKey) as Promise<T>;
    }

    const requestData = Array.isArray(data) ? data[0] : data;

    const requestPromise = axiosInstance
      .post<T>(url, requestData, config)
      .then(data => {
        return data as T;
      })
      .finally(() => {
        pendingRequests.delete(requestKey);
      });

    pendingRequests.set(requestKey, requestPromise);

    return requestPromise;
  },
  put: <T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<T> => {
    const requestConfig = { ...config, url, method: 'put', data };
    const requestKey = generateRequestKey(requestConfig);

    if (pendingRequests.has(requestKey)) {
      return pendingRequests.get(requestKey) as Promise<T>;
    }

    const requestPromise = axiosInstance
      .put<T>(url, data, config)
      .then(data => {
        return data as T;
      })
      .finally(() => {
        pendingRequests.delete(requestKey);
      });

    pendingRequests.set(requestKey, requestPromise);

    return requestPromise;
  },
  delete: <T = any>(url: string, config?: AxiosRequestConfig): Promise<T> => {
    const requestConfig = { ...config, url, method: 'delete' };
    const requestKey = generateRequestKey(requestConfig);

    if (pendingRequests.has(requestKey)) {
      return pendingRequests.get(requestKey) as Promise<T>;
    }

    const requestPromise = axiosInstance.delete<T>(url, config).then(data => {
      return data as T;
    }).finally(() => {
      pendingRequests.delete(requestKey);
    });

    pendingRequests.set(requestKey, requestPromise);

    return requestPromise;
  },
  interceptors: axiosInstance.interceptors,
} as RequestInstance;

export default request;
