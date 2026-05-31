<template>
  <div class="space-y-6">
    <!-- 欢迎信息
    <div class="bg-white shadow rounded-lg p-6">
      <div>
        <h2 class="text-2xl font-bold text-gray-900">欢迎，{{ userStore.userInfo?.real_name || '组织助理' }}</h2>
        <p class="text-gray-600 mt-2">您当前的身份是：组织助理</p>
        <p class="text-gray-600 mt-1">以下是您被授权管理的组织列表</p>
      </div>
    </div> -->

    <!-- 快捷操作 -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="bg-white shadow rounded-lg p-6">
        <div class="flex items-center">
          <div class="flex-shrink-0 bg-green-100 rounded-full p-3">
            <svg
              class="h-6 w-6 text-green-600"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"
              />
            </svg>
          </div>
          <div class="ml-4">
            <h3 class="text-lg font-medium text-gray-900">成长值录入</h3>
            <p class="text-sm text-gray-500">为授权组织成员录入成长值</p>
            <router-link
              to="/assistant/growth"
              class="mt-2 inline-block text-sm font-medium text-primary-600 hover:text-primary-500"
            >
              立即录入
            </router-link>
          </div>
        </div>
      </div>

      <div class="bg-white shadow rounded-lg p-6">
        <div class="flex items-center">
          <div class="flex-shrink-0 bg-blue-100 rounded-full p-3">
            <svg
              class="h-6 w-6 text-blue-600"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
              />
            </svg>
          </div>
          <div class="ml-4">
            <h3 class="text-lg font-medium text-gray-900">成长记录</h3>
            <p class="text-sm text-gray-500">查看您录入的成长记录</p>
            <router-link
              to="/assistant/growth"
              class="mt-2 inline-block text-sm font-medium text-primary-600 hover:text-primary-500"
            >
              查看记录
            </router-link>
          </div>
        </div>
      </div>

      <div class="bg-white shadow rounded-lg p-6">
        <div class="flex items-center">
          <div class="flex-shrink-0 bg-purple-100 rounded-full p-3">
            <svg
              class="h-6 w-6 text-purple-600"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
              />
            </svg>
          </div>
          <div class="ml-4">
            <h3 class="text-lg font-medium text-gray-900">意见征集</h3>
            <p class="text-sm text-gray-500">参与组织意见征集</p>
            <router-link
              to="/assistant/suggestion-forum"
              class="mt-2 inline-block text-sm font-medium text-primary-600 hover:text-primary-500"
            >
              查看征集
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- 授权组织列表 -->
    <div class="bg-white shadow rounded-lg p-6">
      <h3 class="text-lg font-semibold text-gray-900 mb-4">授权组织</h3>
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th
                scope="col"
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                组织名称
              </th>
              <th
                scope="col"
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                状态
              </th>
              <th
                scope="col"
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                操作
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="classItem in classes" :key="classItem.id">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">
                  {{ classItem.school_name }} {{ classItem.session }}级 {{ classItem.class_name }}班
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full"
                  :class="classItem.status ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                >
                  {{ classItem.status ? '正常' : '已关闭' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <router-link
                  :to="`/assistant/students?class_id=${classItem.id}&class_name=${encodeURIComponent(classItem.school_name + classItem.session + '级' + classItem.class_name + '班')}`"
                  class="text-primary-600 hover:text-primary-500 mr-3"
                >
                  查看成员
                </router-link>
                <router-link
                  :to="`/assistant/growth?class_id=${classItem.id}`"
                  class="text-primary-600 hover:text-primary-500"
                >
                  成长管理
                </router-link>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="classes.length === 0" class="text-center py-8">
        <p class="text-gray-500">暂无授权组织</p>
      </div>
    </div>

    <!-- 切换身份/组织模态框 -->
    <div v-if="showRoleModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold text-gray-900">切换身份/组织</h3>
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
          <!-- 切换组织助理身份 -->
          <div>
            <h4 class="text-sm font-medium text-gray-700 mb-2">当前身份：组织助理</h4>
            <div class="space-y-2">
              <div
                v-for="cls in classes"
                :key="cls.id"
                class="p-3 border border-gray-200 rounded-md bg-gray-50 cursor-default"
              >
                <p class="text-sm font-medium text-gray-900">
                  {{ cls.school_name }} {{ cls.session }}级 {{ cls.class_name }}班
                </p>
              </div>
            </div>
          </div>

          <!-- 切换成员身份 -->
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
                <p class="text-xs text-gray-500">
                  学号: {{ cls.student_no_in_class }}
                </p>
              </div>
            </div>
          </div>

          <!-- 没有成员身份时 -->
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
          <button
            @click="submitBindClass"
            class="w-full btn-primary py-2"
          >
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
            id="qr-code-scanner-assistant"
            class="w-full aspect-square bg-gray-100 rounded-lg mb-4"
          ></div>
          <p class="text-sm text-gray-600 text-center">
            请将组织二维码置于扫描框内
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
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { getUserAssistantClasses } from '@/api/class';
import { Html5Qrcode } from 'html5-qrcode';
import request from '@/api/request';

const router = useRouter();
const classes = ref<any[]>([]);
const isAlsoStudent = ref(false);
const showRoleModal = ref(false);
const studentClasses = ref<any[]>([]);

// 绑定组织相关
const showBindClassModal = ref(false);
const showScanner = ref(false);
const bindClassId = ref('');
const bindNameInClass = ref('');
const bindStudentNoInClass = ref('');
let html5Qrcode: Html5Qrcode | null = null;

// 检查用户是否同时也是成员
const checkStudentStatus = async () => {
  try {
    // 检查用户是否有成员绑定记录
    const response = await request.get('/api/v1/students/my-classes');
    if (response && Array.isArray(response) && response.length > 0) {
      isAlsoStudent.value = true;
      studentClasses.value = response;
    } else {
      isAlsoStudent.value = false;
      studentClasses.value = [];
    }
  } catch (error) {
    console.error('检查成员状态失败:', error);
    isAlsoStudent.value = false;
    studentClasses.value = [];
  }
};

// 选择切换到特定组织的成员身份
const selectStudentClass = (cls: any) => {
  showRoleModal.value = false;
  localStorage.setItem('selectedRole', 'student');
  localStorage.setItem('selectedClassId', cls.id.toString());
  router.push('/student');
};

// 打开绑定组织弹窗
const openBindClassModal = () => {
  showBindClassModal.value = true;
};

// 关闭绑定组织弹窗
const closeBindClassModal = () => {
  showBindClassModal.value = false;
};

// 提交绑定组织
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

  // 解析二维码内容
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
    // 验证二维码是否有效
    try {
      await request.get(`/api/v1/classes/qr/${qrCode}`);
    } catch (error: any) {
      console.error('验证组织信息失败:', error);
      alert('无效的组织二维码内容或组织不存在');
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
      // 重新检查成员状态
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

// 在绑定弹窗中打开扫码器
const openScannerInBindModal = async () => {
  showBindClassModal.value = false;
  showScanner.value = true;

  // 等待 DOM 更新后初始化扫码器
  setTimeout(async () => {
    try {
      html5Qrcode = new Html5Qrcode('qr-code-scanner-assistant');

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
      alert('无效的组织二维码');
      return;
    }

    // 通过 qr_code 获取组织信息
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

    // 填充组织二维码内容并重新打开绑定弹窗
    bindClassId.value = result;
    showBindClassModal.value = true;
  } catch (error) {
    console.error('处理扫码结果失败:', error);
    alert('处理扫码结果失败，请稍后重试');
  }
};

const fetchClasses = async () => {
  try {
    const data = await getUserAssistantClasses();
    classes.value = (data as any).items || [];
  } catch (error) {
    console.error('获取授权组织失败:', error);
    classes.value = [];
  }
};

onMounted(async () => {
  await fetchClasses();
  await checkStudentStatus();
});
</script>
