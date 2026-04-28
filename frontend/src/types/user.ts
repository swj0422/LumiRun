export interface UserInfo {
  id: number;
  email: string;
  real_name: string;
  phone?: string;
  role_id: number;
  role_name: string;
  status: boolean;
  last_login_time?: string;
  login_count: number;
  created_at: string;
}

export interface LoginForm {
  username: string;
  password: string;
  captcha?: string;
}

export interface RegisterForm {
  email: string;
  username: string;
  password: string;
  real_name: string;
  role_id: number;
}

export interface LoginResponse {
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: UserInfo;
  is_class_assistant: boolean;
  assistant_classes: number[];
}

export interface PasswordForm {
  old_password: string;
  new_password: string;
}
