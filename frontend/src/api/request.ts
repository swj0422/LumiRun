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

// 确保baseURL不会被覆盖
axiosInstance.defaults.baseURL = '';

// 包装axios实例，添加合并重复请求的功能
const request = {
  get: <T = any>(url: string, config?: AxiosRequestConfig): Promise<T> => {
    const requestConfig = { ...config, url, method: 'get' };
    const requestKey = generateRequestKey(requestConfig);

    // 检查是否有相同的请求正在进行
    if (pendingRequests.has(requestKey)) {
      return pendingRequests.get(requestKey) as Promise<T>;
    }

    // 创建新的请求
    const requestPromise = axiosInstance.get<T>(url, config).then(data => {
      return data as T;
    }).finally(() => {
      // 请求完成后从pendingRequests中移除
      pendingRequests.delete(requestKey);
    });

    // 存储请求
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

    // 检查是否有相同的请求正在进行
    if (pendingRequests.has(requestKey)) {
      return pendingRequests.get(requestKey) as Promise<T>;
    }

    // 确保数据是对象而不是数组
    const requestData = Array.isArray(data) ? data[0] : data;

    // 创建新的请求
    const requestPromise = axiosInstance
      .post<T>(url, requestData, config)
      .then(data => {
        return data as T;
      })
      .finally(() => {
        // 请求完成后从pendingRequests中移除
        pendingRequests.delete(requestKey);
      });

    // 存储请求
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

    // 检查是否有相同的请求正在进行
    if (pendingRequests.has(requestKey)) {
      return pendingRequests.get(requestKey) as Promise<T>;
    }

    // 创建新的请求
    const requestPromise = axiosInstance
      .put<T>(url, data, config)
      .then(data => {
        return data as T;
      })
      .finally(() => {
        // 请求完成后从pendingRequests中移除
        pendingRequests.delete(requestKey);
      });

    // 存储请求
    pendingRequests.set(requestKey, requestPromise);

    return requestPromise;
  },
  delete: <T = any>(url: string, config?: AxiosRequestConfig): Promise<T> => {
    const requestConfig = { ...config, url, method: 'delete' };
    const requestKey = generateRequestKey(requestConfig);

    // 检查是否有相同的请求正在进行
    if (pendingRequests.has(requestKey)) {
      return pendingRequests.get(requestKey) as Promise<T>;
    }

    // 创建新的请求
    const requestPromise = axiosInstance.delete<T>(url, config).then(data => {
      return data as T;
    }).finally(() => {
      // 请求完成后从pendingRequests中移除
      pendingRequests.delete(requestKey);
    });

    // 存储请求
    pendingRequests.set(requestKey, requestPromise);

    return requestPromise;
  },
  interceptors: axiosInstance.interceptors,
} as RequestInstance;

// 请求拦截器
axiosInstance.interceptors.request.use(
  (config) => {
    let token = getTokenFromCookie();
    console.log('[DEBUG] Request interceptor token:', token);
    // 登录请求不需要Authorization头
    const isLoginRequest = config.url?.includes('/auth/login');
    console.log('[DEBUG] Is login request:', isLoginRequest);
    // 对于 FormData 请求，不设置 Content-Type，让浏览器自动处理
    if (config.data instanceof FormData) {
      if (config.headers) {
        delete config.headers['Content-Type'];
      }
    }
    // 添加 Authorization 头（在删除 Content-Type 头之后，确保 Authorization 头存在）
    if (token && !isLoginRequest) {
      // 确保 headers 对象存在
      if (!config.headers) {
        config.headers = {} as any;
      }
      // 使用普通对象赋值添加 Authorization 头
      config.headers!['Authorization'] = `Bearer ${token}`;
      console.log('[DEBUG] Added Authorization header:', config.headers['Authorization']);
    }
    console.log('[DEBUG] Request config:', config);
    console.log('[DEBUG] Request data:', config.data);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
axiosInstance.interceptors.response.use(
  (response: AxiosResponse) => {
    // 确保返回的数据格式一致
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
          // 不要在这里重定向，让路由守卫处理登录逻辑
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

    // 统一错误格式，便于前端处理
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

export default request;
