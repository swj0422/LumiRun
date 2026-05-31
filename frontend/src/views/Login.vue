<template>
  <div
    class="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-primary-100 py-12 px-4 sm:px-6 lg:px-8"
  >
    <div class="max-w-md w-full space-y-8">
      <div class="text-center">
        <div
          class="mx-auto h-16 w-16 bg-primary-600 rounded-full flex items-center justify-center"
        >
          <svg
            class="h-8 w-8 text-white"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M13 10V3L4 14h7v7l9-11h-7z"
            />
          </svg>
        </div>
        <h2 class="mt-6 text-3xl font-extrabold text-gray-900">逐光成长系统</h2>
        <p class="mt-2 text-sm text-gray-600">
          LumiRun - 每一步成长都值得被看见
        </p>
      </div>

      <div class="card p-8">
        <form class="space-y-6" @submit.prevent="handleLogin">
          <div>
            <label for="username" class="label">用户名</label>
            <input
              id="username"
              v-model="form.username"
              type="text"
              required
              class="input"
              placeholder="请输入用户名或邮箱"
            />
          </div>

          <div>
            <label for="password" class="label">密码</label>
            <div class="relative">
              <input
                id="password"
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                required
                class="input pr-10"
                placeholder="请输入密码"
              />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
              >
                <svg
                  v-if="!showPassword"
                  class="h-5 w-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                  />
                </svg>
                <svg
                  v-else
                  class="h-5 w-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"
                  />
                </svg>
              </button>
            </div>
          </div>

          <div v-if="needCaptcha" class="flex gap-3">
            <div class="flex-1">
              <label for="captcha" class="label">验证码</label>
              <input
                id="captcha"
                v-model="form.captcha"
                type="text"
                required
                class="input"
                placeholder="请输入验证码"
              />
            </div>
            <div class="flex-shrink-0">
              <label class="label">&nbsp;</label>
              <img
                :src="captchaImage"
                @click="refreshCaptcha"
                class="h-10 w-24 border rounded cursor-pointer hover:opacity-80"
                alt="验证码"
              />
            </div>
          </div>

          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <input
                id="remember-me"
                v-model="rememberMe"
                type="checkbox"
                class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label for="remember-me" class="ml-2 block text-sm text-gray-900">
                记住我
              </label>
            </div>
            <div class="text-sm">
              <router-link
                to="/forgot-password"
                class="font-medium text-primary-600 hover:text-primary-500"
              >
                忘记密码？
              </router-link>
            </div>
          </div>

          <div v-if="errorMsg" class="text-red-500 text-sm text-center">
            {{ errorMsg }}
          </div>

          <div>
            <button
              type="submit"
              :disabled="loading"
              class="btn-primary w-full"
            >
              <span v-if="loading">登录中...</span>
              <span v-else>登录</span>
            </button>
          </div>
        </form>

        <div class="mt-6">
          <div class="relative">
            <div class="absolute inset-0 flex items-center">
              <div class="w-full border-t border-gray-300"></div>
            </div>
            <div class="relative flex justify-center text-sm">
              <span class="px-2 bg-white text-gray-500"> 还没有账号？ </span>
            </div>
          </div>

          <div class="mt-6 grid grid-cols-2 gap-3">
            <router-link
              to="/register?role=student"
              class="btn-secondary w-full text-center"
            >
              成员注册
            </router-link>
            <router-link
              to="/register?role=teacher"
              class="btn-secondary w-full text-center"
            >
              管理者注册
            </router-link>
          </div>
        </div>
      </div>

      <div class="text-center text-xs text-gray-500">
        <p>Lesimple System</p>
        <p class="mt-1">欢迎关注公众号繁乐简</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import request from '@/api/request';
import { useUserStore } from '@/stores/user';
import { onMounted, reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { checkUserAssistantStatus } from '@/api/class';

const router = useRouter();
const userStore = useUserStore();

const loading = ref(false);
const rememberMe = ref(false);
const showPassword = ref(false);
const needCaptcha = ref(false);
const captchaImage = ref('');
const captchaId = ref('');
const errorMsg = ref('');

const form = reactive({
  username: '',
  password: '',
  captcha: '',
});

const refreshCaptcha = async () => {
  try {
    const data = await request.get('/api/v1/auth/captcha');
    captchaImage.value = (data as any).captcha_image;
    captchaId.value = (data as any).captcha_id;
  } catch (error) {
    console.error('获取验证码失败:', error);
  }
};

const handleLogin = async () => {
  console.log('[DEBUG] handleLogin called');
  if (!form.username || !form.password) {
    errorMsg.value = '请填写完整信息';
    return;
  }

  if (needCaptcha.value && !form.captcha) {
    errorMsg.value = '请输入验证码';
    return;
  }

  loading.value = true;
  errorMsg.value = '';

  try {
    console.log('[DEBUG] Preparing login request');
    const headers: Record<string, string> = {};
    if (needCaptcha.value && captchaId.value) {
      headers['X-Captcha-Id'] = captchaId.value;
    }

    console.log('[DEBUG] Calling userStore.loginAction');
    const res = await userStore.loginAction(
      {
        username: form.username,
        password: form.password,
        captcha: needCaptcha.value ? form.captcha : undefined,
      },
      headers
    );

    console.log('[DEBUG] Login response in handleLogin:', res);

    if (!res || !res.user) {
      throw new Error('登录响应格式不正确，缺少用户信息');
    }

    console.log('[DEBUG] User role:', res.user.role_name);
    console.log('[DEBUG] Current cookies:', document.cookie);

    // 登录成功后刷新页面，确保Cookie生效
    setTimeout(() => {
      if (res.user.role_name === 'admin' || res.user.role_name === 'super_admin') {
        window.location.href = '/admin';
      } else if (res.user.role_name === 'teacher') {
        window.location.href = '/teacher';
      } else if (res.user.role_name === 'student') {
        if (res.is_class_assistant) {
          window.location.href = '/role-selection';
        } else {
          window.location.href = '/student';
        }
      } else {
        window.location.href = '/';
      }
    }, 500);
  } catch (error: any) {
    console.error('[DEBUG] Login error:', error);
    if (error.response?.status === 429) {
      needCaptcha.value = true;
      errorMsg.value = '请输入验证码';
      refreshCaptcha();
    } else {
      const data = error.response?.data;
      if (Array.isArray(data)) {
        const messages: Record<string, string> = {
          'value is not a valid email address': '邮箱格式不正确',
          'field required': '请填写完整信息',
        };
        const detail = data[0]?.msg || '';
        errorMsg.value = messages[detail] || '请检查输入信息';
      } else {
        errorMsg.value =
          data?.detail || error.message || '登录失败，请检查邮箱和密码';
      }
    }
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  refreshCaptcha();
});
</script>