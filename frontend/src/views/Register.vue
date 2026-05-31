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
        <h2 class="text-3xl font-extrabold text-gray-900">用户注册</h2>
        <p class="mt-2 text-sm text-gray-600">加入逐光成长系统</p>
      </div>

      <div class="card p-6">
        <label class="label">选择角色</label>
        <div class="grid grid-cols-2 gap-4 mt-2">
          <button
            @click="form.role_id = 4"
            class="p-4 border-2 rounded-lg text-center transition-all"
            :class="
              form.role_id === 4
                ? 'border-primary-500 bg-primary-50'
                : 'border-gray-200'
            "
          >
            <div class="text-2xl mb-2">🎓</div>
            <div class="font-medium">成员</div>
            <div class="text-xs text-gray-500 mt-1">无需审核，直接可用</div>
          </button>
          <button
            @click="form.role_id = 3"
            class="p-4 border-2 rounded-lg text-center transition-all"
            :class="
              form.role_id === 3
                ? 'border-primary-500 bg-primary-50'
                : 'border-gray-200'
            "
          >
            <div class="text-2xl mb-2">👨‍🏫</div>
            <div class="font-medium">管理者</div>
            <div class="text-xs text-gray-500 mt-1">需要管理员审核</div>
          </button>
        </div>
      </div>

      <div class="card p-8">
        <form class="space-y-6" @submit.prevent="handleRegister">
          <div>
            <label for="email" class="label"
              >邮箱 <span class="text-red-500">*</span></label
            >
            <input
              id="email"
              v-model="form.email"
              type="email"
              required
              class="input"
              placeholder="请输入邮箱（用于找回密码）"
            />
          </div>

          <div>
            <label for="username" class="label"
              >用户名 <span class="text-red-500">*</span></label
            >
            <input
              id="username"
              v-model="form.username"
              type="text"
              required
              class="input"
              placeholder="请输入用户名（登录账号）"
            />
            <p class="text-xs text-gray-500 mt-1">用户名至少3位</p>
          </div>

          <div>
            <label for="real_name" class="label"
              >真实姓名 <span class="text-red-500">*</span></label
            >
            <input
              id="real_name"
              v-model="form.real_name"
              type="text"
              required
              class="input"
              placeholder="请输入真实姓名"
            />
          </div>

          <div>
            <label for="password" class="label"
              >密码 <span class="text-red-500">*</span></label
            >
            <input
              id="password"
              v-model="form.password"
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
            <label for="confirm_password" class="label"
              >确认密码 <span class="text-red-500">*</span></label
            >
            <input
              id="confirm_password"
              v-model="confirmPassword"
              type="password"
              required
              class="input"
              placeholder="请再次输入密码"
            />
          </div>

          <div v-if="errorMsg" class="text-red-500 text-sm text-center">
            {{ errorMsg }}
          </div>

          <div class="flex items-center">
            <input
              id="agree-terms"
              v-model="agreeTerms"
              type="checkbox"
              class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            />
            <label for="agree-terms" class="ml-2 block text-sm text-gray-900">
              我已阅读并同意
              <a href="#" class="text-primary-600">《用户协议》</a> 和
              <a href="#" class="text-primary-600">《隐私政策》</a>
            </label>
          </div>

          <div>
            <button
              type="submit"
              :disabled="loading || !agreeTerms"
              class="btn-primary w-full"
            >
              <span v-if="loading">注册中...</span>
              <span v-else>注册</span>
            </button>
          </div>
        </form>
      </div>

      <div class="text-center text-sm text-gray-500">
        <p>
          已有账号？<router-link
            to="/login"
            class="text-primary-600 hover:text-primary-700"
            >立即登录</router-link
          >
        </p>
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
        <h3 class="text-xl font-bold text-gray-900 mb-2">注册成功！</h3>
        <p class="text-gray-600 mb-6">{{ successMessage }}</p>
        <router-link to="/login" class="btn-primary w-full">
          去登录
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useUserStore } from '@/stores/user';
import { onMounted, reactive, ref } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const userStore = useUserStore();

const loading = ref(false);
const confirmPassword = ref('');
const agreeTerms = ref(false);
const showSuccessModal = ref(false);
const successMessage = ref('');
const errorMsg = ref('');

const form = reactive({
  email: '',
  username: '',
  real_name: '',
  password: '',
  role_id: 4,
});

onMounted(() => {
  const role = route.query.role;
  if (role === 'teacher') {
    form.role_id = 3;
  } else if (role === 'student') {
    form.role_id = 4;
  }
});

const validatePassword = (password: string): boolean => {
  if (password.length < 6) return false;
  const hasUpper = /[A-Z]/.test(password);
  const hasLower = /[a-z]/.test(password);
  return hasUpper && hasLower;
};

const handleRegister = async () => {
  errorMsg.value = '';

  if (!agreeTerms.value) {
    errorMsg.value = '请阅读并同意用户协议';
    return;
  }

  if (form.password !== confirmPassword.value) {
    errorMsg.value = '两次输入的密码不一致';
    return;
  }

  if (!validatePassword(form.password)) {
    errorMsg.value = '密码至少6位，必须包含大写和小写字母';
    return;
  }

  loading.value = true;
  try {
    const res = await userStore.registerAction({
      email: form.email,
      username: form.username,
      password: form.password,
      real_name: form.real_name,
      role_id: form.role_id,
    });

    successMessage.value = res.need_approval
      ? '注册成功！请等待管理员审核后登录。'
      : '注册成功！请使用邮箱和密码登录。';

    showSuccessModal.value = true;
  } catch (error: any) {
    const data = error.response?.data;
    if (Array.isArray(data)) {
      const messages: Record<string, string> = {
        'value is not a valid email address': '邮箱格式不正确',
        'field required': '请填写完整信息',
        'String should have at least 3 characters': '用户名至少3位',
      };
      const detail = data[0]?.msg || '';
      errorMsg.value = messages[detail] || '请检查输入信息';
    } else {
      errorMsg.value = data?.detail || '注册失败，请稍后重试';
    }
  } finally {
    loading.value = false;
  }
};
</script>
