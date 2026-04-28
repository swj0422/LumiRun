<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 顶部导航栏 -->
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <!-- 第一行：Logo和用户信息 -->
        <div class="flex justify-between h-16">
          <!-- Logo -->
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
              <span class="text-sm text-gray-700">班级助理: {{ studentName || userStore.userInfo?.real_name }}</span>
              <!-- 切换班级/学员按钮 -->
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
            <!-- 切换班级/学员按钮 -->
            <button
              @click="showRoleModal = true; mobileMenuOpen = false"
              class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50"
            >
              切换班级/学员
            </button>
            <div class="px-3 py-2">
              <div class="flex items-center justify-between">
                <span class="text-base font-medium text-gray-700">班级助理: {{ studentName || userStore.userInfo?.real_name }}</span>
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

    <!-- 切换身份/班级模态框 -->
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
          <!-- 切换班级助理身份 -->
          <div>
            <h4 class="text-sm font-medium text-gray-700 mb-2">当前身份：班级助理</h4>
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

          <!-- 切换学员身份 -->
          <div v-if="isAlsoStudent">
            <h4 class="text-sm font-medium text-gray-700 mb-2">切换为学员身份</h4>
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
                <p class="text-xs text-gray-500">
                  学号: {{ cls.student_no_in_class }}
                </p>
              </div>
            </div>
          </div>

          <!-- 没有学员身份时 -->
          <div v-else class="text-center py-4">
            <p class="text-gray-500 text-sm mb-4">暂无绑定的学员班级</p>
            <button 
              @click="openBindClassModal"
              class="w-full py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              去绑定新班级
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 绑定班级弹窗 -->
    <div v-if="showBindClassModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold text-gray-900">绑定班级</h3>
          <button
            @click="closeBindClassModal"
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
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">班级二维码内容</label>
            <div class="flex items-center space-x-2">
              <input
                v-model="bindClassId"
                type="text"
                placeholder="请输入班级二维码内容（class:xxx格式）"
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
            <label class="block text-sm font-medium text-gray-700 mb-1">班级内姓名</label>
            <input
              v-model="bindNameInClass"
              type="text"
              placeholder="请输入老师给的名字"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">班级内学号</label>
            <input
              v-model="bindStudentNoInClass"
              type="text"
              placeholder="请输入老师给的学号"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <button
            @click="submitBindClass"
            class="w-full btn-primary py-2"
          >
            绑定班级
          </button>
        </div>
      </div>
    </div>

    <!-- 扫码弹窗 -->
    <div v-if="showScanner" class="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50">
      <div class="relative w-full max-w-md">
        <div class="bg-white rounded-lg p-4">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-semibold text-gray-900">扫描班级码</h3>
            <button
              @click="closeScanner"
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
          <div
            id="qr-code-scanner-assistant-layout"
            class="w-full aspect-square bg-gray-100 rounded-lg mb-4"
          ></div>
          <p class="text-sm text-gray-600 text-center">
            请将班级二维码置于扫描框内
          </p>
          <div class="mt-4 flex justify-center">
            <button @click="closeScanner" class="text-sm text-primary-600">
              取消
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
import { Html5Qrcode } from 'html5-qrcode';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();
const mobileMenuOpen = ref(false);
const showRoleModal = ref(false);
const assistantClasses = ref<any[]>([]);
const studentClasses = ref<any[]>([]);
const isAlsoStudent = ref(false);
const studentName = ref('');

// 绑定班级相关
const showBindClassModal = ref(false);
const showScanner = ref(false);
const bindClassId = ref('');
const bindNameInClass = ref('');
const bindStudentNoInClass = ref('');
let html5Qrcode: Html5Qrcode | null = null;

// 获取班级助理的授权班级
const fetchAssistantClasses = async () => {
  try {
    const response = await request.get('/api/v1/class-assistants/user');
    if (response && Array.isArray(response)) {
      assistantClasses.value = response;
    }
  } catch (error) {
    console.error('获取授权班级失败:', error);
    assistantClasses.value = [];
  }
};

// 检查用户是否同时也是学员
const checkStudentStatus = async () => {
  try {
    const response = await request.get('/api/v1/students/my-classes');
    if (response && Array.isArray(response) && response.length > 0) {
      isAlsoStudent.value = true;
      studentClasses.value = response;
      // 使用第一个绑定班级的学员名字
      studentName.value = response[0].student_name || '';
    } else {
      isAlsoStudent.value = false;
      studentClasses.value = [];
      studentName.value = '';
    }
  } catch (error) {
    console.error('检查学员状态失败:', error);
    isAlsoStudent.value = false;
    studentClasses.value = [];
    studentName.value = '';
  }
};

// 选择切换到特定班级的学员身份
const selectStudentClass = (cls: any) => {
  showRoleModal.value = false;
  localStorage.setItem('selectedRole', 'student');
  localStorage.setItem('selectedClassId', cls.id.toString());
  router.push('/student');
};

// 打开绑定班级弹窗
const openBindClassModal = () => {
  showBindClassModal.value = true;
};

// 关闭绑定班级弹窗
const closeBindClassModal = () => {
  showBindClassModal.value = false;
};

// 提交绑定班级
const submitBindClass = async () => {
  if (!bindClassId.value) {
    alert('请输入班级二维码内容');
    return;
  }
  if (!bindNameInClass.value) {
    alert('请输入班级内姓名');
    return;
  }
  if (!bindStudentNoInClass.value) {
    alert('请输入班级内学号');
    return;
  }

  // 解析二维码内容
  let qrCode = '';
  if (bindClassId.value.startsWith('class:')) {
    qrCode = bindClassId.value.substring(6);
  } else {
    qrCode = bindClassId.value;
  }

  if (!qrCode) {
    alert('无效的班级二维码内容');
    return;
  }

  try {
    // 验证二维码是否有效
    try {
      await request.get(`/api/v1/classes/qr/${qrCode}`);
    } catch (error: any) {
      console.error('验证班级信息失败:', error);
      alert('无效的班级二维码内容或班级不存在');
      return;
    }

    // 调用绑定接口
    const bindData = {
      qr_code: qrCode,
      name_in_class: bindNameInClass.value,
      student_no_in_class: bindStudentNoInClass.value,
    };

    const response = await request.post('/api/v1/students/bind', bindData);

    if (response.message === '绑定成功') {
      alert('绑定成功！');
      closeBindClassModal();
      // 重新检查学员状态
      await checkStudentStatus();
    } else if (response.message === '绑定申请已提交，请等待导师审批') {
      alert('绑定申请已提交，请等待导师审批');
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

// 在绑定弹窗中打开扫码器
const openScannerInBindModal = async () => {
  showBindClassModal.value = false;
  showScanner.value = true;

  // 等待 DOM 更新后初始化扫码器
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

// 关闭扫码器
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

// 处理扫码结果
const handleScanResult = async (result: string) => {
  try {
    // 停止扫码
    if (html5Qrcode) {
      await html5Qrcode.stop();
      html5Qrcode = null;
    }

    // 关闭扫码弹窗
    showScanner.value = false;

    // 解析扫码结果
    // 二维码内容格式: class:{qr_code}
    let qrCode = '';
    if (result.startsWith('class:')) {
      qrCode = result.substring(6);
    } else {
      qrCode = result;
    }

    if (!qrCode) {
      alert('无效的班级二维码');
      return;
    }

    // 通过 qr_code 获取班级信息
    let classInfo;
    try {
      classInfo = await request.get(`/api/v1/classes/qr/${qrCode}`);
    } catch (error: any) {
      console.error('获取班级信息失败:', error);
      alert('无效的班级二维码或班级不存在');
      return;
    }

    if (!classInfo || !classInfo.id) {
      alert('无效的班级二维码或班级不存在');
      return;
    }

    // 填充班级二维码内容并重新打开绑定弹窗
    bindClassId.value = result;
    showBindClassModal.value = true;
  } catch (error) {
    console.error('处理扫码结果失败:', error);
    alert('处理扫码结果失败，请稍后重试');
  }
};

// 页面加载时检查用户状态
onMounted(async () => {
  await fetchAssistantClasses();
  await checkStudentStatus();
});

const navItems = computed(() => {
  return [
    { name: '首页', path: '/assistant' },
    { name: '学员管理', path: '/assistant/students' },
    { name: '成长管理', path: '/assistant/growth' },
    { name: '意见征集', path: '/assistant/suggestion-forum' },
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
