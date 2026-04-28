import { getCurrentUser, login, register } from '@/api/auth';
import type { LoginForm, RegisterForm, UserInfo } from '@/types/user';
import { defineStore } from 'pinia';
import { computed, ref } from 'vue';

// 从Cookie或localStorage中获取token
function getTokenFromCookie() {
  // 先尝试从Cookie中获取token（访问令牌存储在Cookie中）
  const cookie = document.cookie;
  const cookieArray = cookie.split(';');
  for (const item of cookieArray) {
    const [name, value] = item.trim().split('=');
    if (name === 'token') {
      return value;
    }
  }
  
  // 再尝试从localStorage中获取token
  const tokenFromLocalStorage = localStorage.getItem('token');
  if (tokenFromLocalStorage) {
    return tokenFromLocalStorage;
  }
  
  return null;
}

// 清除Cookie中的token
function clearTokenFromCookie() {
  document.cookie = 'token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
}

// 缓存相关函数
function getCache(key: string) {
  try {
    const value = localStorage.getItem(key);
    return value ? JSON.parse(value) : null;
  } catch (error) {
    console.error('获取缓存失败:', error);
    return null;
  }
}

function setCache(key: string, value: any) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch (error) {
    console.error('设置缓存失败:', error);
  }
}

function removeCache(key: string) {
  try {
    localStorage.removeItem(key);
  } catch (error) {
    console.error('删除缓存失败:', error);
  }
}

function clearCache() {
  try {
    localStorage.clear();
  } catch (error) {
    console.error('清空缓存失败:', error);
  }
}

export const useUserStore = defineStore('user', () => {
  const token = ref<string>(getTokenFromCookie());
  const userInfo = ref<UserInfo | null>(getCache('userInfo'));
  const loading = ref(false);
  const menus = ref<any[]>(getCache('menus') || []);
  const permissions = ref<string[]>(getCache('permissions') || []);
  const baseConfig = ref<any>(getCache('baseConfig') || {});

  const isLoggedIn = computed(() => !!userInfo.value);
  const isAdmin = computed(
    () =>
      userInfo.value?.role_name === 'super_admin' ||
      userInfo.value?.role_name === 'admin'
  );
  const isTeacher = computed(() => userInfo.value?.role_name === 'teacher');
  const isStudent = computed(() => userInfo.value?.role_name === 'student');
  const isClassAssistant = computed(() => userInfo.value?.role_name === 'class_assistant');

  const setToken = (newToken: string) => {
    token.value = newToken;
  };

  const clearToken = () => {
    token.value = '';
    userInfo.value = null;
    menus.value = [];
    permissions.value = [];
    baseConfig.value = {};
    clearTokenFromCookie();
    clearCache();
  };

  const loginAction = async (
    form: LoginForm,
    headers?: Record<string, string>
  ) => {
    loading.value = true;
    try {
      const res = await login(form, headers);
      // 确保res和res.user存在
      if (!res || !res.user) {
        throw new Error('登录响应格式不正确，缺少用户信息');
      }
      // 从Cookie中获取访问令牌
      const tokenFromCookie = getTokenFromCookie();
      if (tokenFromCookie) {
        token.value = tokenFromCookie;
      } else {
        // 尝试从响应中获取token
        const tokenFromResponse = res.refresh_token || '';
        if (tokenFromResponse) {
          token.value = tokenFromResponse;
          localStorage.setItem('token', tokenFromResponse);
        }
      }
      userInfo.value = res.user;

      // 缓存用户信息
      setCache('userInfo', res.user);

      // 保存助理信息到localStorage
      if (res.is_class_assistant) {
        localStorage.setItem('isClassAssistant', 'true');
        if (res.assistant_classes) {
          localStorage.setItem('assistantClasses', JSON.stringify(res.assistant_classes));
        }
      } else {
        localStorage.removeItem('isClassAssistant');
        localStorage.removeItem('assistantClasses');
      }

      // 这里可以根据实际情况获取菜单、权限和基础配置
      // 假设登录响应中包含这些信息
      if (res.menus) {
        menus.value = res.menus;
        setCache('menus', res.menus);
      }
      if (res.permissions) {
        permissions.value = res.permissions;
        setCache('permissions', res.permissions);
      }
      if (res.baseConfig) {
        baseConfig.value = res.baseConfig;
        setCache('baseConfig', res.baseConfig);
      }

      return res;
    } catch (error) {
      console.error('登录失败:', error);
      throw error;
    } finally {
      loading.value = false;
    }
  };

  const registerAction = async (form: RegisterForm) => {
    loading.value = true;
    try {
      const res = await register(form);
      return res;
    } finally {
      loading.value = false;
    }
  };

  const fetchUserInfo = async () => {
    try {
      // 优先从缓存中获取
      const cachedUserInfo = getCache('userInfo');
      if (cachedUserInfo) {
        userInfo.value = cachedUserInfo;
      }

      // 从缓存中获取菜单、权限和基础配置
      const cachedMenus = getCache('menus');
      if (cachedMenus) {
        menus.value = cachedMenus;
      }

      const cachedPermissions = getCache('permissions');
      if (cachedPermissions) {
        permissions.value = cachedPermissions;
      }

      const cachedBaseConfig = getCache('baseConfig');
      if (cachedBaseConfig) {
        baseConfig.value = cachedBaseConfig;
      }

      // 从服务器获取最新数据
      const res = await getCurrentUser();
      userInfo.value = res;
      token.value = getTokenFromCookie(); // 从Cookie中获取token

      // 更新缓存
      setCache('userInfo', res);

      // 假设getCurrentUser返回包含菜单、权限和基础配置
      if (res.menus) {
        menus.value = res.menus;
        setCache('menus', res.menus);
      }
      if (res.permissions) {
        permissions.value = res.permissions;
        setCache('permissions', res.permissions);
      }
      if (res.baseConfig) {
        baseConfig.value = res.baseConfig;
        setCache('baseConfig', res.baseConfig);
      }
    } catch (error) {
      console.error('获取用户信息失败:', error);
      // 不清除token，保持用户登录状态
      throw error;
    }
  };

  const logout = () => {
    clearToken();
  };

  return {
    token,
    userInfo,
    loading,
    menus,
    permissions,
    baseConfig,
    isLoggedIn,
    isAdmin,
    isTeacher,
    isStudent,
    isClassAssistant,
    setToken,
    clearToken,
    loginAction,
    registerAction,
    fetchUserInfo,
    logout,
  };
});
