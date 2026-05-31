<template>
  <div class="min-h-screen bg-gray-50 flex">
    <!-- 侧边栏导航 -->
    <aside
      :class="[
        'hidden md:flex flex-col bg-white border-r border-gray-200 fixed left-0 top-0 h-screen transition-all duration-300 z-40',
        sidebarCollapsed ? 'w-16' : 'w-56'
      ]"
    >
      <!-- Logo区域 -->
      <div class="flex items-center h-16 px-4 border-b border-gray-200">
        <router-link to="/assistant" class="flex items-center flex-1">
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
          <span v-if="!sidebarCollapsed" class="ml-2 text-lg font-bold text-gray-900 truncate">逐光成长系统</span>
        </router-link>
        <button
          @click="sidebarCollapsed = !sidebarCollapsed"
          class="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md"
          :title="sidebarCollapsed ? '展开菜单' : '收起菜单'"
        >
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path v-if="sidebarCollapsed" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
          </svg>
        </button>
      </div>

      <!-- 导航菜单 -->
      <nav class="flex-1 py-4">
        <div class="space-y-1 px-2">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="flex items-center justify-center px-3 py-2 text-sm font-medium rounded-md"
            :class="isActive(item.path) ? 'text-primary-600 bg-primary-50 border-l-2 border-primary-600' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'"
          >
            <svg class="w-5 h-5 flex-shrink-0" :class="sidebarCollapsed ? '' : 'mr-3'" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path v-if="item.name === '首页'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              <path v-else-if="item.name === '成员管理'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
              <path v-else-if="item.name === '成长管理'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              <path v-else-if="item.name === '意见征集'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              <path v-else-if="item.name === '心愿便利贴'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            <span v-if="!sidebarCollapsed" class="truncate">{{ item.name }}</span>
          </router-link>
        </div>
      </nav>

      <!-- 用户信息和操作 -->
      <div class="px-3 py-3 border-t border-gray-200">
        <div v-if="!sidebarCollapsed" class="flex items-center justify-between mb-2">
          <span class="text-sm text-gray-700 truncate flex-1">组织助理: {{ studentName || userStore.userInfo?.real_name }}</span>
          <button
            @click="showRoleModal = true"
            class="flex items-center text-sm text-gray-500 hover:text-gray-700 ml-2"
          >
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
          </button>
        </div>
        <div class="flex items-center justify-between">
          <button
            v-if="!sidebarCollapsed"
            @click="handleLogout"
            class="text-sm text-gray-500 hover:text-gray-700"
          >
            退出
          </button>
          <button
            v-else
            @click="handleLogout"
            class="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md"
            title="退出"
          >
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
          </button>
        </div>
      </div>
    </aside>

    <!-- 移动端顶部导航栏 -->
    <header class="md:hidden bg-white shadow-sm border-b border-gray-200 fixed top-0 left-0 right-0 z-50">
      <div class="flex justify-between h-16 px-4">
        <div class="flex items-center">
          <router-link to="/assistant" class="flex items-center">
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
            <span class="ml-2 text-xl font-bold text-gray-900">逐光成长系统</span>
          </router-link>
        </div>

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

      <div v-if="mobileMenuOpen" class="py-4 border-t border-gray-200 px-4">
        <div class="space-y-2">
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
          <button 
            @click="showRoleModal = true; mobileMenuOpen = false"
            class="block w-full px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50 text-left"
          >
            切换组织/成员
          </button>
          <div class="pt-4 border-t border-gray-200">
            <div class="flex items-center justify-between">
              <span class="text-base font-medium text-gray-700">组织助理: {{ studentName || userStore.userInfo?.real_name }}</span>
              <button @click="handleLogout" class="text-base font-medium text-gray-500 hover:text-gray-700">退出</button>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- 主内容区 -->
    <main :class="['flex-1 transition-all duration-300', sidebarCollapsed ? 'md:ml-16' : 'md:ml-56']">
      <div class="max-w-6xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </main>

    <!-- 切换身份/组织模态框 -->
    <div v-if="showRoleModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold text-gray-900">切换身份/组织</h3>
          <button @click="showRoleModal = false" class="text-gray-500 hover:text-gray-700">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="space-y-4">
          <div>
            <h4 class="text-sm font-medium text-gray-700 mb-2">当前身份：组织助理</h4>
            <div class="space-y-2">
              <div
                v-for="cls in assistantClasses"
                :key="cls.id"
                class="p-3 border border-gray-200 rounded-md bg-gray-50 cursor-default"
              >
                <p class="text-sm font-medium text-gray-900">
                  {{ cls.school_name ? cls.school_name + ' ' : '' }}{{ cls.session }}级 {{ cls.class_name }}班
                </p>
              </div>
            </div>
          </div>

          <div v-if="isAlsoStudent">
            <h4 class="text-sm font-medium text-gray-700 mb-2">切换为成员身份</h4>
            <div class="space-y-2">
              <div
                v-for="cls in studentClasses"
                :key="cls.id"
                @click="selectStudentClass(cls)"
                class="p-3 border border-blue-200 rounded-md hover:bg-blue-50 cursor-pointer"
              >
                <p class="text-sm font-medium text-gray-900">
                  {{ cls.school_name ? cls.school_name + ' ' : '' }}{{ cls.session }}级 {{ cls.class_name }}班
                </p>
                <p class="text-xs text-gray-500">学号: {{ cls.student_no_in_class }}</p>
              </div>
            </div>
          </div>

          <div v-else class="text-center py-4">
            <p class="text-gray-500 text-sm mb-4">暂无绑定的成员组织</p>
            <button 
              @click="openBindClassModal"
              class="w-full py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              去绑定新组织
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 绑定组织弹窗 -->
    <div v-if="showBindClassModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold text-gray-900">绑定组织</h3>
          <button @click="closeBindClassModal" class="text-gray-500 hover:text-gray-700">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">组织二维码内容</label>
            <div class="flex items-center space-x-2">
              <input
                v-model="bindClassId"
                type="text"
                placeholder="请输入组织二维码内容（class:xxx格式）"
                class="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
              <button
                @click="openScannerInBindModal"
                class="p-2 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200"
                title="扫码填写"
              >
                <svg class="w-5 h-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z" />
                </svg>
              </button>
            </div>
            <p class="text-xs text-gray-500 mt-1">二维码内容通常以"class:"开头</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">组织内姓名</label>
            <input
              v-model="bindNameInClass"
              type="text"
              placeholder="请输入老师给的名字"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">组织内学号</label>
            <input
              v-model="bindStudentNoInClass"
              type="text"
              placeholder="请输入老师给的学号"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <button @click="submitBindClass" class="w-full btn-primary py-2">
            绑定组织
          </button>
        </div>
      </div>
    </div>

    <!-- 扫码弹窗 -->
    <div v-if="showScanner" class="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50">
      <div class="relative w-full max-w-md">
        <div class="bg-white rounded-lg p-4">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-semibold text-gray-900">扫描组织码</h3>
            <button @click="closeScanner" class="text-gray-500 hover:text-gray-700">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div id="qr-code-scanner-assistant-layout" class="w-full aspect-square bg-gray-100 rounded-lg mb-4"></div>
          <p class="text-sm text-gray-600 text-center">请将组织二维码置于扫描框内</p>
          <div class="mt-4 flex justify-center">
            <button @click="closeScanner" class="text-sm text-primary-600">取消</button>
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
import { Html5Qrcode } from 'html5-qrcode';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();
const mobileMenuOpen = ref(false);
const sidebarCollapsed = ref(false);
const showRoleModal = ref(false);
const assistantClasses = ref<any[]>([]);
const studentClasses = ref<any[]>([]);
const isAlsoStudent = ref(false);
const studentName = ref('');

const showBindClassModal = ref(false);
const showScanner = ref(false);
const bindClassId = ref('');
const bindNameInClass = ref('');
const bindStudentNoInClass = ref('');
let html5Qrcode: Html5Qrcode | null = null;

const fetchAssistantClasses = async () => {
  try {
    const response = await request.get('/api/v1/class-assistants/user');
    if (response && Array.isArray(response)) {
      assistantClasses.value = response;
    }
  } catch (error) {
    console.error('获取授权组织失败:', error);
    assistantClasses.value = [];
  }
};

const checkStudentStatus = async () => {
  try {
    const response = await request.get('/api/v1/students/my-classes');
    if (response && Array.isArray(response) && response.length > 0) {
      isAlsoStudent.value = true;
      studentClasses.value = response;
      studentName.value = response[0].student_name || '';
    } else {
      isAlsoStudent.value = false;
      studentClasses.value = [];
      studentName.value = '';
    }
  } catch (error) {
    console.error('检查成员状态失败:', error);
    isAlsoStudent.value = false;
    studentClasses.value = [];
    studentName.value = '';
  }
};

const selectStudentClass = (cls: any) => {
  showRoleModal.value = false;
  localStorage.setItem('selectedRole', 'student');
  localStorage.setItem('selectedClassId', cls.id.toString());
  router.push('/student');
};

const openBindClassModal = () => {
  showBindClassModal.value = true;
};

const closeBindClassModal = () => {
  showBindClassModal.value = false;
};

const submitBindClass = async () => {
  if (!bindClassId.value) {
    alert('请输入组织二维码内容');
    return;
  }
  if (!bindNameInClass.value) {
    alert('请输入组织内姓名');
    return;
  }
  if (!bindStudentNoInClass.value) {
    alert('请输入组织内学号');
    return;
  }

  let qrCode = '';
  if (bindClassId.value.startsWith('class:')) {
    qrCode = bindClassId.value.substring(6);
  } else {
    qrCode = bindClassId.value;
  }

  if (!qrCode) {
    alert('无效的组织二维码内容');
    return;
  }

  try {
    try {
      await request.get(`/api/v1/classes/qr/${qrCode}`);
    } catch (error: any) {
      console.error('验证组织信息失败:', error);
      alert('无效的组织二维码内容或组织不存在');
      return;
    }

    const bindData = {
      qr_code: qrCode,
      name_in_class: bindNameInClass.value,
      student_no_in_class: bindStudentNoInClass.value,
    };

    const response = await request.post('/api/v1/students/bind', bindData);

    if (response.message === '绑定成功') {
      alert('绑定成功！');
      closeBindClassModal();
      await checkStudentStatus();
    } else if (response.message === '绑定申请已提交，请等待管理者审批') {
      alert('绑定申请已提交，请等待管理者审批');
      closeBindClassModal();
    } else {
      alert('绑定失败：' + (response.message || '未知错误'));
    }
  } catch (error: any) {
    console.error('绑定失败:', error);
    const errorMessage = error?.response?.data?.detail || error?.message || '绑定失败，请稍后重试';
    alert(errorMessage);
  }
};

const openScannerInBindModal = async () => {
  showBindClassModal.value = false;
  showScanner.value = true;

  setTimeout(async () => {
    try {
      html5Qrcode = new Html5Qrcode('qr-code-scanner-assistant-layout');

      await html5Qrcode.start(
        { facingMode: 'environment' },
        { fps: 10, qrbox: { width: 250, height: 250 } },
        (decodedText) => {
          handleScanResult(decodedText);
        },
        (errorMessage) => {
          console.log('扫码错误:', errorMessage);
        }
      );
    } catch (error) {
      console.error('初始化扫码器失败:', error);
      alert('无法访问摄像头，请检查权限设置');
      closeScanner();
    }
  }, 100);
};

const closeScanner = async () => {
  showScanner.value = false;

  if (html5Qrcode) {
    try {
      await html5Qrcode.stop();
    } catch (error) {
      console.error('停止扫码器失败:', error);
    }
    html5Qrcode = null;
  }
};

const handleScanResult = async (result: string) => {
  try {
    if (html5Qrcode) {
      await html5Qrcode.stop();
      html5Qrcode = null;
    }

    showScanner.value = false;

    let qrCode = '';
    if (result.startsWith('class:')) {
      qrCode = result.substring(6);
    } else {
      qrCode = result;
    }

    if (!qrCode) {
      alert('无效的组织二维码');
      return;
    }

    let classInfo;
    try {
      classInfo = await request.get(`/api/v1/classes/qr/${qrCode}`);
    } catch (error: any) {
      console.error('获取组织信息失败:', error);
      alert('无效的组织二维码或组织不存在');
      return;
    }

    if (!classInfo || !classInfo.id) {
      alert('无效的组织二维码或组织不存在');
      return;
    }

    bindClassId.value = result;
    showBindClassModal.value = true;
  } catch (error) {
    console.error('处理扫码结果失败:', error);
    alert('处理扫码结果失败，请稍后重试');
  }
};

onMounted(async () => {
  await fetchAssistantClasses();
  await checkStudentStatus();
});

const navItems = computed(() => {
  return [
    { name: '首页', path: '/assistant' },
    { name: '成员管理', path: '/assistant/students' },
    { name: '成长管理', path: '/assistant/growth' },
    { name: '意见征集', path: '/assistant/suggestion-forum' },
    { name: '心愿便利贴', path: '/assistant/wish-wall' },
  ];
});

const isActive = (path: string) => {
  if (path === '/assistant') {
    return route.path === '/assistant';
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
