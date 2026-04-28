<template>
  <div class="space-y-6">
    <div class="bg-white shadow rounded-lg p-6">
      <h1 class="text-2xl font-bold text-gray-900 mb-6">个人中心</h1>
      
      <div class="mb-6">
        <h2 class="text-lg font-semibold text-gray-800 mb-4">个人信息</h2>
        <div class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">姓名</label>
              <input 
                v-model="userInfo.real_name"
                type="text" 
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">手机号</label>
              <input 
                v-model="userInfo.phone"
                type="tel" 
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">邮箱</label>
            <input 
              v-model="userInfo.email"
              type="email" 
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div class="mt-6">
            <button 
              @click="updateProfile"
              class="w-full bg-primary-600 text-white py-2 rounded-md hover:bg-primary-700"
            >
              保存修改
            </button>
          </div>
        </div>
      </div>

      <div class="mb-4">
        <h2 class="text-lg font-semibold text-gray-800 mb-4">安全设置</h2>
        <div class="space-y-4">
          <div class="flex justify-between items-center p-3 border border-gray-200 rounded-lg">
            <span class="text-sm text-gray-700">修改密码</span>
            <button 
              @click="openChangePassword"
              class="px-3 py-1 bg-gray-100 text-gray-700 text-xs rounded-md hover:bg-gray-200"
            >
              点击修改
            </button>
          </div>
        </div>
      </div>

      <div class="mb-4">
        <h2 class="text-lg font-semibold text-gray-800 mb-4">其他</h2>
        <div class="space-y-4">
          <div class="flex justify-between items-center p-3 border border-gray-200 rounded-lg">
            <span class="text-sm text-gray-700">关于系统</span>
            <button 
              @click="showAbout = true"
              class="px-3 py-1 bg-gray-100 text-gray-700 text-xs rounded-md hover:bg-gray-200"
            >
              查看
            </button>
          </div>
          <div class="flex justify-between items-center p-3 border border-gray-200 rounded-lg">
            <span class="text-sm text-red-600">退出登录</span>
            <button 
              @click="logout"
              class="px-3 py-1 bg-red-100 text-red-700 text-xs rounded-md hover:bg-red-200"
            >
              退出
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 关于系统弹窗 -->
    <div v-if="showAbout" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold text-gray-900">关于系统</h3>
          <button @click="showAbout = false" class="text-gray-500 hover:text-gray-700">
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="space-y-4">
          <div class="text-center">
            <h4 class="text-xl font-bold text-gray-900 mb-2">逐光成长系统</h4>
            <p class="text-sm text-gray-600">LumiRun</p>
          </div>
          <div class="space-y-2">
            <div class="flex justify-between">
              <span class="text-sm text-gray-600">版本</span>
              <span class="text-sm font-medium text-gray-900">1.0.0</span>
            </div>
            <div class="flex justify-between">
              <span class="text-sm text-gray-600">开发者</span>
              <span class="text-sm font-medium text-gray-900">逐光团队</span>
            </div>
            <div class="flex justify-between">
              <span class="text-sm text-gray-600">联系邮箱</span>
              <span class="text-sm font-medium text-gray-900">contact@lumi.run</span>
            </div>
          </div>
          <p class="text-sm text-gray-600 text-center">
            逐光成长系统是一款专为导师和学员设计的轻量化成长管理工具，帮助记录和管理学员的成长历程。
          </p>
          <button @click="showAbout = false" class="w-full mt-4 px-4 py-2 bg-primary-600 text-white text-sm rounded-md hover:bg-primary-700">
            确定
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import request from '@/api/request';
import { onMounted, ref } from 'vue';
import { useUserStore } from '@/stores/user';

const userStore = useUserStore();

const userInfo = ref({
  real_name: '',
  phone: '',
  email: '',
});

const showAbout = ref(false);

const fetchUserInfo = async () => {
  try {
    const response = await request.get('/api/v1/user/info');
    if (response) {
      userInfo.value = {
        real_name: response.real_name || '',
        phone: response.phone || '',
        email: response.email || '',
      };
    }
  } catch (error) {
    console.error('获取用户信息失败:', error);
  }
};

const updateProfile = async () => {
  try {
    const response = await request.put('/api/v1/user/update', userInfo.value);
    if (response && response.message === '更新成功') {
      alert('更新成功！');
      // 重新获取用户信息
      await userStore.fetchUserInfo();
    } else {
      alert('更新失败：' + (response?.message || '未知错误'));
    }
  } catch (error) {
    console.error('更新用户信息失败:', error);
    alert('更新失败，请稍后重试');
  }
};

const openChangePassword = () => {
  // 这里可以打开修改密码的弹窗
  alert('修改密码功能开发中');
};

const logout = async () => {
  if (confirm('确定要退出登录吗？')) {
    try {
      await request.post('/api/v1/auth/logout');
      userStore.logout();
      // 跳转到登录页面
      window.location.href = '/login';
    } catch (error) {
      console.error('退出登录失败:', error);
      // 即使失败也强制退出
      userStore.logout();
      window.location.href = '/login';
    }
  }
};

onMounted(async () => {
  await fetchUserInfo();
});
</script>