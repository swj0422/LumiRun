import type {
  LoginForm,
  LoginResponse,
  RegisterForm,
  UserInfo,
} from '@/types/user';
import request from './request';

export const login = (
  data: LoginForm,
  headers?: Record<string, string>
): Promise<LoginResponse> => {
  console.log('[DEBUG] Login request data:', data);
  console.log('[DEBUG] Login request headers:', headers);
  console.log('[DEBUG] Current cookies before login:', document.cookie);

  return request.post('/api/v1/auth/login', data, { headers }).then((response) => {
    console.log('[DEBUG] Login response data:', response);
    console.log('[DEBUG] Current cookies after login:', document.cookie);
    return response;
  }) as Promise<LoginResponse>;
};

export const register = (
  data: RegisterForm
): Promise<{ message: string; user_id: number; need_approval: boolean }> => {
  return request.post('/api/v1/auth/register', data) as Promise<{
    message: string;
    user_id: number;
    need_approval: boolean;
  }>;
};

export const getCurrentUser = (): Promise<UserInfo> => {
  return request.get('/api/v1/auth/me') as Promise<UserInfo>;
};

export const changePassword = (data: {
  old_password: string;
  new_password: string;
}): Promise<{ message: string }> => {
  return request.put('/api/v1/users/password', data) as Promise<{
    message: string;
  }>;
};

export const forgotPassword = (
  email: string
): Promise<{ message: string; debug_link?: string }> => {
  return request.post('/api/v1/auth/forgot-password', { email }) as Promise<{
    message: string;
    debug_link?: string;
  }>;
};

export const resetPassword = (
  token: string,
  new_password: string
): Promise<{ message: string }> => {
  return request.post('/api/v1/auth/reset-password', {
    token,
    new_password,
  }) as Promise<{ message: string }>;
};

export const getCaptcha = (): Promise<{
  captcha_id: string;
  captcha_image: string;
}> => {
  return request.get('/api/v1/auth/captcha') as Promise<{
    captcha_id: string;
    captcha_image: string;
  }>;
};
