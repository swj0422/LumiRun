<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 顶部导航栏 -->
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <!-- 第一行：Logo和用户信息 -->
        <div class="flex justify-between h-16">
          <!-- Logo -->
          <div class="flex items-center">
            <router-link to="/student" class="flex items-center">
              <div
                class="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center"
              >
                <svg
                  class="w-5 h-5 text-white"
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
              <span class="ml-2 text-xl font-bold text-gray-900"
                >逐光成长系统</span
              >
            </router-link>
          </div>

          <!-- 移动端菜单按钮 -->
          <div class="md:hidden flex items-center">
            <button
              @click="mobileMenuOpen = !mobileMenuOpen"
              class="p-2 rounded-md text-gray-500 hover:text-gray-700 hover:bg-gray-100"
            >
              <svg
                class="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  v-if="!mobileMenuOpen"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M4 6h16M4 12h16M4 18h16"
                />
                <path
                  v-else
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>

          <!-- 用户信息 -->
          <div class="hidden md:flex items-center">
            <div class="flex items-center space-x-4">
              <span class="text-sm text-gray-700">学员: {{ studentName || userStore.userInfo?.real_name }}</span>
              <!-- 切换班级/助理按钮 -->
              <button 
                @click="showRoleModal = true"
                class="flex items-center text-sm text-gray-500 hover:text-gray-700"
              >
                <svg class="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                切换
              </button>
              <button
                @click="handleLogout"
                class="text-sm text-gray-500 hover:text-gray-700"
              >
                退出
              </button>
            </div>
          </div>
        </div>

        <!-- 第二行：导航菜单 -->
        <nav class="hidden md:flex space-x-8 h-12 items-center">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="inline-flex items-center px-1 pt-1 text-sm font-medium"
            :class="isActive(item.path) ? 'text-primary-600 border-b-2 border-primary-600' : 'text-gray-500 hover:text-gray-700'"
          >
            {{ item.name }}
          </router-link>
        </nav>

        <!-- 移动端导航菜单 -->
        <div
          v-if="mobileMenuOpen"
          class="md:hidden py-4 border-t border-gray-200"
        >
          <div class="space-y-4">
            <router-link
              v-for="item in navItems"
              :key="item.path"
              :to="item.path"
              @click="mobileMenuOpen = false"
              class="block px-3 py-2 rounded-md text-base font-medium"
              :class="isActive(item.path) ? 'text-primary-600 bg-primary-50' : 'text-gray-700 hover:text-gray-900 hover:bg-gray-50'"
            >
              {{ item.name }}
            </router-link>
            <!-- 切换班级/助理按钮 -->
            <button 
              @click="showRoleModal = true; mobileMenuOpen = false"
              class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50"
            >
              切换班级/助理
            </button>
            <div class="px-3 py-2">
              <div class="flex items-center justify-between">
                <span class="text-base font-medium text-gray-700">学员: {{ studentName || userStore.userInfo?.real_name }}</span>
                <button
                  @click="handleLogout"
                  class="text-base font-medium text-gray-500 hover:text-gray-700"
                >
                  退出
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <!-- 切换班级/助理模态框 -->
    <div v-if="showRoleModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold text-gray-900">切换身份/班级</h3>
          <button
            @click="showRoleModal = false"
            class="text-gray-500 hover:text-gray-700"
          >
            <svg
              class="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>
        <div class="space-y-4">
          <!-- 切换班级 -->
          <div>
            <h4 class="text-sm font-medium text-gray-700 mb-2">我的班级</h4>
            <div class="space-y-2">
              <div
                v-for="cls in bindClasses"
                :key="cls.id"
                class="p-3 border border-gray-200 rounded-md hover:bg-gray-50 cursor-pointer"
              >
                <p class="text-sm font-medium text-gray-900">
                  {{ cls.school_name ? cls.school_name + ' ' : '' }}{{ cls.session }}级 {{ cls.class_name }}班
                </p>
                <p class="text-xs text-gray-500">
                  学号: {{ cls.student_no_in_class }}
                </p>
              </div>
            </div>

          </div>
          
          <!-- 切换助理身份 -->
          <div v-if="hasAssistantRole">
            <h4 class="text-sm font-medium text-gray-700 mb-2">其他身份</h4>
            <button 
              @click="switchToAssistant"
              class="w-full py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
            >
              切换到班级助理身份
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useUserStore } from '@/stores/user';
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import request from '@/api/request';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();
const mobileMenuOpen = ref(false);
const showRoleModal = ref(false);
const bindClasses = ref<any[]>([]);
const hasAssistantRole = ref(false);
const studentName = ref('');

// 获取学员名字（从绑定班级信息中获取）
const getStudentName = async () => {
  try {
    console.log('[DEBUG] getStudentName 开始获取学员名字');
    const response = await request.get('/api/v1/students/my-classes');
    console.log('[DEBUG] getStudentName API 响应:', response);
    console.log('[DEBUG] getStudentName 响应类型:', typeof response);
    console.log('[DEBUG] getStudentName 是否为数组:', Array.isArray(response));
    if (response && Array.isArray(response) && response.length > 0) {
      console.log('[DEBUG] getStudentName 第一个班级信息:', response[0]);
      console.log('[DEBUG] getStudentName 学员名字:', response[0].student_name);
      // 使用绑定班级中的学员名字
      studentName.value = response[0].student_name || userStore.userInfo?.real_name || '';
      console.log('[DEBUG] getStudentName 设置学员名字:', studentName.value);
    } else {
      console.log('[DEBUG] getStudentName 没有绑定班级，使用账号名字');
      studentName.value = userStore.userInfo?.real_name || '';
    }
  } catch (error) {
    console.error('获取学员名字失败:', error);
    studentName.value = userStore.userInfo?.real_name || '';
  }
};

// 检查用户的班级和助理身份
const checkUserStatus = async () => {
  try {
    console.log('[DEBUG] checkUserStatus 开始检查用户状态');
    // 检查绑定的班级
    const response = await request.get('/api/v1/students/my-classes');
    console.log('[DEBUG] checkUserStatus 绑定班级响应:', response);
    if (response && Array.isArray(response)) {
      bindClasses.value = response;
      console.log('[DEBUG] checkUserStatus 已设置绑定班级数量:', response.length);
    }
    
    // 检查是否有班级助理身份
    const assistantStatus = await request.get('/api/v1/class-assistants/user/check');
    console.log('[DEBUG] checkUserStatus 助理状态响应:', assistantStatus);
    hasAssistantRole.value = (assistantStatus as any).has_assistant_role || false;
    console.log('[DEBUG] checkUserStatus 是否为助理:', hasAssistantRole.value);
  } catch (error) {
    console.error('检查用户状态失败:', error);
  }
};

// 打开绑定班级弹窗
const openBindClass = () => {
  showRoleModal.value = false;
  // 使用 sessionStorage 来传递打开绑定弹窗的指令
  sessionStorage.setItem('openBindModal', 'true');
  router.push('/student');
};

// 切换到班级助理身份
const switchToAssistant = () => {
  showRoleModal.value = false;
  localStorage.setItem('selectedRole', 'class_assistant');
  router.push('/assistant');
};

// 页面加载时检查用户状态
onMounted(async () => {
  await checkUserStatus();
  await getStudentName();
});

const navItems = computed(() => {
  return [
    { name: '首页', path: '/student' },
    { name: '成长值', path: '/student/growth' },
    { name: '奖励', path: '/student/shop' },
    { name: '订单', path: '/student/orders' },
    { name: '排名', path: '/student/rank' },
    { name: '意见征集', path: '/student/forum' },
  ];
});

const isActive = (path: string) => {
  if (path === '/student') {
    return route.path === '/student';
  }
  return route.path === path || route.path.startsWith(path + '/');
};

const handleLogout = () => {
  userStore.logout();
  router.push('/login');
};
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>