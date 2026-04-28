<template>
  <div
    class="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-primary-100 py-12 px-4 sm:px-6 lg:px-8"
  >
    <div class="max-w-md w-full space-y-8">
      <div class="text-center">
        <router-link
          to="/login"
          class="inline-flex items-center text-primary-600 hover:text-primary-700 mb-4"
        >
          <svg
            class="w-5 h-5 mr-1"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M15 19l-7-7 7-7"
            />
          </svg>
          返回登录
        </router-link>
        <h2 class="text-3xl font-extrabold text-gray-900">重置密码</h2>
        <p class="mt-2 text-sm text-gray-600">请设置您的新密码</p>
      </div>

      <div class="card p-8">
        <form class="space-y-6" @submit.prevent="handleSubmit">
          <div>
            <label for="password" class="label">新密码</label>
            <input
              id="password"
              v-model="password"
              type="password"
              required
              class="input"
              placeholder="至少6位，包含大小写字母"
            />
            <p class="text-xs text-gray-500 mt-1">
              密码要求：至少6位，必须包含大写和小写字母
            </p>
          </div>

          <div>
            <label for="confirm_password" class="label">确认密码</label>
            <input
              id="confirm_password"
              v-model="confirmPassword"
              type="password"
              required
              class="input"
              placeholder="请再次输入新密码"
            />
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
              <span v-if="loading">重置中...</span>
              <span v-else>重置密码</span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <div
      v-if="showSuccessModal"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg p-8 max-w-sm mx-4 text-center">
        <div
          class="w-16 h-16 bg-success-100 rounded-full flex items-center justify-center mx-auto mb-4"
        >
          <svg
            class="w-8 h-8 text-success-600"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M5 13l4 4L19 7"
            />
          </svg>
        </div>
        <h3 class="text-xl font-bold text-gray-900 mb-2">密码重置成功！</h3>
        <p class="text-gray-600 mb-6">请使用新密码登录</p>
        <router-link to="/login" class="btn-primary w-full">
          去登录
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { resetPassword } from '@/api/auth';

const route = useRoute();

const token = ref('');
const password = ref('');
const confirmPassword = ref('');
const loading = ref(false);
const errorMsg = ref('');
const showSuccessModal = ref(false);

onMounted(() => {
  token.value = (route.query.token as string) || '';
  if (!token.value) {
    errorMsg.value = '无效的重置链接';
  }
});

const validatePassword = (pwd: string): boolean => {
  if (pwd.length < 6) return false;
  const hasUpper = /[A-Z]/.test(pwd);
  const hasLower = /[a-z]/.test(pwd);
  return hasUpper && hasLower;
};

const handleSubmit = async () => {
  errorMsg.value = '';

  if (!token.value) {
    errorMsg.value = '无效的重置链接';
    return;
  }

  if (password.value !== confirmPassword.value) {
    errorMsg.value = '两次输入的密码不一致';
    return;
  }

  if (!validatePassword(password.value)) {
    errorMsg.value = '密码至少6位，必须包含大写和小写字母';
    return;
  }

  loading.value = true;
  try {
    await resetPassword(token.value, password.value);
    showSuccessModal.value = true;
  } catch (error: any) {
    errorMsg.value = error.response?.data?.detail || '重置失败，请稍后重试';
  } finally {
    loading.value = false;
  }
};
</script>
