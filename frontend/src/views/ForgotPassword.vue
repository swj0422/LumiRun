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
        <h2 class="text-3xl font-extrabold text-gray-900">忘记密码</h2>
        <p class="mt-2 text-sm text-gray-600">
          输入注册邮箱，我们将发送重置链接
        </p>
      </div>

      <div class="card p-8">
        <form class="space-y-6" @submit.prevent="handleSubmit">
          <div>
            <label for="email" class="label">注册邮箱</label>
            <input
              id="email"
              v-model="email"
              type="email"
              required
              class="input"
              placeholder="请输入注册时使用的邮箱"
            />
          </div>

          <div v-if="errorMsg" class="text-red-500 text-sm text-center">
            {{ errorMsg }}
          </div>

          <div v-if="successMsg" class="text-green-600 text-sm text-center">
            {{ successMsg }}
          </div>

          <div>
            <button
              type="submit"
              :disabled="loading"
              class="btn-primary w-full"
            >
              <span v-if="loading">发送中...</span>
              <span v-else>发送重置链接</span>
            </button>
          </div>
        </form>

        <div v-if="resetLink" class="mt-6 p-4 bg-gray-50 rounded-lg">
          <p class="text-sm text-gray-600 mb-2">开发环境 - 重置链接：</p>
          <router-link
            :to="`/reset-password?token=${resetToken}`"
            class="text-primary-600 text-sm break-all hover:underline"
          >
            {{ resetLink }}
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { forgotPassword } from '@/api/auth';

const email = ref('');
const loading = ref(false);
const errorMsg = ref('');
const successMsg = ref('');
const resetLink = ref('');
const resetToken = ref('');

const handleSubmit = async () => {
  if (!email.value) {
    errorMsg.value = '请输入邮箱';
    return;
  }

  loading.value = true;
  errorMsg.value = '';
  successMsg.value = '';

  try {
    const res = await forgotPassword(email.value);
    successMsg.value = res.message;

    if (res.debug_link) {
      const token = res.debug_link.split('token=')[1];
      resetToken.value = token;
      resetLink.value = res.debug_link;
    }
  } catch (error: any) {
    errorMsg.value = error.response?.data?.detail || '发送失败，请稍后重试';
  } finally {
    loading.value = false;
  }
};
</script>
