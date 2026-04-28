<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 绑定班级信息 -->
    <div v-if="hasBindClass && bindClassInfo" class="px-4 py-3 bg-primary-50 border-b border-primary-100">
      <div>
        <p class="text-xs text-primary-600">已绑定班级</p>
        <div class="flex items-center">
          <p class="text-sm font-medium text-primary-800">
            {{ bindClassInfo.school_name }} {{ bindClassInfo.session }}级 {{ bindClassInfo.class_name }}班
          </p>
          <div class="text-xs text-primary-600 ml-2">
            学号: {{ bindClassInfo.student_no_in_class }}
          </div>
        </div>
      </div>
    </div>

    <!-- 成长值卡片 -->
    <div class="px-4 -mt-4">
      <div class="card p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-gray-500 text-sm">可用成长值</p>
            <p class="text-3xl font-bold text-primary-600 mt-1">
              {{ hasBindClass ? growthScore.available_score : 0 }}
            </p>
          </div>
          <div class="text-right">
            <p class="text-gray-500 text-sm">累计成长值</p>
            <p class="text-xl font-semibold text-gray-800 mt-1">
              {{ hasBindClass ? growthScore.total_score : 0 }}
            </p>
          </div>
        </div>
        <div v-if="hasBindClass" class="mt-4 flex space-x-3">
          <router-link
            to="/student/growth"
            class="btn-primary flex-1 text-center text-sm py-2"
          >
            查看明细
          </router-link>
          <router-link
            to="/student/shop"
            class="btn-success flex-1 text-center text-sm py-2"
          >
            去兑换
          </router-link>
        </div>
      </div>
    </div>

    <!-- 快捷入口 -->
    <div v-if="hasBindClass" class="px-4 mt-6">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">快捷入口</h2>
      <div class="grid grid-cols-2 gap-4">
        <router-link to="/student/growth" class="card p-4 hover:shadow-md transition-shadow">
          <div class="flex items-center">
            <div class="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
              <svg class="w-6 h-6 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">我的成长记录</p>
            </div>
          </div>
        </router-link>
        <router-link to="/student/shop" class="card p-4 hover:shadow-md transition-shadow">
          <div class="flex items-center">
            <div class="w-12 h-12 bg-success-100 rounded-lg flex items-center justify-center">
              <svg class="w-6 h-6 text-success-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">我要兑换礼品</p>
            </div>
          </div>
        </router-link>
        <router-link to="/student/rank" class="card p-4 hover:shadow-md transition-shadow">
          <div class="flex items-center">
            <div class="w-12 h-12 bg-warning-100 rounded-lg flex items-center justify-center">
              <svg class="w-6 h-6 text-warning-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">班级排行榜</p>
            </div>
          </div>
        </router-link>
        <router-link to="/student/forum" class="card p-4 hover:shadow-md transition-shadow">
          <div class="flex items-center">
            <div class="w-12 h-12 bg-info-100 rounded-lg flex items-center justify-center">
              <svg class="w-6 h-6 text-info-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">意见征集</p>
            </div>
          </div>
        </router-link>
        <router-link to="/student/wishes" class="card p-4 hover:shadow-md transition-shadow">
          <div class="flex items-center">
            <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <svg class="w-6 h-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">心愿墙</p>
            </div>
          </div>
        </router-link>
      </div>
    </div>

    <!-- 最新动态 -->
    <div v-if="hasBindClass" class="px-4 mt-6">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">最新动态</h2>
      <div class="space-y-3">
        <div
          v-for="(item, index) in recentActivities"
          :key="index"
          class="card p-4"
        >
          <div class="flex items-start space-x-3">
            <div
              :class="`w-8 h-8 ${item.iconBg} rounded-full flex items-center justify-center flex-shrink-0`"
            >
              <component :is="item.icon" class="w-4 h-4 text-white" />
            </div>
            <div class="flex-1">
              <p class="text-sm text-gray-800">{{ item.title }}</p>
              <p class="text-xs text-gray-500 mt-1">{{ item.time }}</p>
            </div>
            <span
              v-if="item.score"
              :class="item.score > 0 ? 'text-success-600' : 'text-danger-600'"
              class="font-semibold"
            >
              {{ item.score > 0 ? '+' : '' }}{{ item.score }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 最近兑换记录 -->
    <div v-if="hasBindClass && recentOrders.length > 0" class="px-4 mt-6">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">最近兑换记录</h2>
      <div class="space-y-3">
        <div
          v-for="(order, index) in recentOrders"
          :key="index"
          class="card p-4"
        >
          <div class="flex items-start space-x-3">
            <div class="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center flex-shrink-0">
              <svg class="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v13m0-13V6a2 2 0 112-2h-2zm0 0V5.5A2.5 2.5 0 109.5 8H12zm-7 4h14M5 12a2 2 0 110-4h14a2 2 0 110 4M5 12v7a2 2 0 002 2h10a2 2 0 002-2v-7" />
              </svg>
            </div>
            <div class="flex-1">
              <p class="text-sm font-medium text-gray-800">{{ order.gift_name }}</p>
              <p class="text-xs text-gray-500 mt-1">
                {{ new Date(order.created_at).toLocaleDateString() }}
              </p>
            </div>
            <div class="text-right">
              <p class="text-sm font-semibold text-gray-800">{{ order.total_point }}</p>
              <span 
                :class="{
                  'text-xs px-2 py-1 rounded-full': true,
                  'bg-green-100 text-green-800': order.status === 'completed',
                  'bg-yellow-100 text-yellow-800': order.status === 'pending',
                  'bg-red-100 text-red-800': order.status === 'cancelled',
                }"
              >
                {{ order.status === 'completed' ? '已完成' : order.status === 'pending' ? '待处理' : '已取消' }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 绑定的班级列表 -->
    <div v-if="hasBindClass && bindClasses.length > 1" class="px-4 mt-6">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">我的班级</h2>
      <div class="space-y-3">
        <div
          v-for="cls in bindClasses"
          :key="cls.id"
          class="card p-4 border border-gray-200 rounded-lg"
        >
          <div class="flex justify-between items-start">
            <div>
              <div class="flex items-center">
                <p class="text-sm font-medium text-gray-900">
                  {{ cls.school_name ? cls.school_name + ' ' : '' }}{{ cls.session }}级 {{ cls.class_name }}班
                </p>
                <span 
                  v-if="cls.bind_status !== 'approved'"
                  :class="{
                    'ml-2 px-2 py-0.5 rounded-full text-xs font-medium': true,
                    'bg-yellow-100 text-yellow-800': cls.bind_status === 'pending',
                    'bg-red-100 text-red-800': cls.bind_status === 'rejected'
                  }"
                >
                  {{ cls.bind_status === 'pending' ? '待审核' : '已拒绝' }}
                </span>
                <div class="text-xs text-primary-600 ml-2">
                  老师: {{ cls.teacher_name }}
                </div>
              </div>
              <p class="text-xs text-gray-500 mt-1">
                学号: {{ cls.student_no_in_class }}
              </p>
              <p class="text-xs text-gray-500 mt-1">
                绑定时间: {{ cls.bind_time ? new Date(cls.bind_time).toLocaleDateString() : '未知' }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 绑定班级提示 -->
    <div v-if="!hasBindClass" class="px-4 mt-6">
      <div class="card p-4 bg-warning-50 border-warning-200">
        <div class="flex items-center">
          <div
            class="w-10 h-10 bg-warning-100 rounded-full flex items-center justify-center flex-shrink-0"
          >
            <svg
              class="w-5 h-5 text-warning-600"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>
          <div class="ml-3 flex-1">
            <p class="text-sm font-medium text-warning-800">尚未绑定班级</p>
            <p class="text-xs text-warning-600 mt-1">
              请扫描导师提供的二维码绑定班级
            </p>
          </div>
          <div class="flex space-x-2">
            <button @click="openScanner" class="btn-primary text-xs py-1 px-3">
              扫码绑定
            </button>
            <button @click="openManualBind" class="btn-secondary text-xs py-1 px-3">
              手动输入
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 扫码弹窗 -->
    <div
      v-if="showScanner"
      class="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50"
    >
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
            id="qr-code-scanner"
            class="w-full aspect-square bg-gray-100 rounded-lg mb-4"
          ></div>
          <p class="text-sm text-gray-600 text-center">
            请将班级二维码置于扫描框内
          </p>
          <div class="mt-4 flex justify-center">
            <button @click="closeScanner; openManualBind()" class="text-sm text-primary-600">
              手动输入班级ID
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 手动绑定弹窗 -->
    <div
      v-if="showManualBind"
      class="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50"
    >
      <div class="relative w-full max-w-md">
        <div class="bg-white rounded-lg p-4">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-semibold text-gray-900">手动绑定班级</h3>
            <button
              @click="closeManualBind"
              class="text-gray-500 hover:text-gray-700"
            >
              <svg
                class="w-6 h-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
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
                  v-model="manualClassId"
                  type="text"
                  placeholder="请输入班级二维码内容（class:xxx格式）"
                  class="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
                <button
                  @click="openScannerInManualBind"
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
                v-model="manualNameInClass"
                type="text"
                placeholder="请输入老师给的名字"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">班级内学号</label>
              <input
                v-model="manualStudentNoInClass"
                type="text"
                placeholder="请输入老师给的学号"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <button
              @click="submitManualBind"
              class="w-full btn-primary py-2"
            >
              绑定班级
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import request from '@/api/request';
import { Html5Qrcode } from 'html5-qrcode';
import { onMounted, ref } from 'vue';
// 导入图标组件

const recentOrders = ref<any[]>([]);

const hasBindClass = ref(false); // 实际应从API获取
const showScanner = ref(false);
const showManualBind = ref(false);
const scannerFromManualBind = ref(false); // 标记扫码是否来自手动绑定弹窗
const manualClassId = ref('');
const manualNameInClass = ref('');
const manualStudentNoInClass = ref('');
let html5Qrcode: Html5Qrcode | null = null;

const growthScore = ref({
  total_score: 0,
  available_score: 0,
});

const bindClassInfo = ref<any>(null); // 绑定班级信息
const bindClasses = ref<any[]>([]); // 所有绑定的班级

const quickLinks = [
  {
    name: '成长值',
    path: '/student/growth',
    icon: 'ChartIcon',
    bgColor: 'bg-primary-500',
  },
  {
    name: '奖励',
    path: '/student/shop',
    icon: 'GiftIcon',
    bgColor: 'bg-success-500',
  },
  {
    name: '订单',
    path: '/student/orders',
    icon: 'ClipboardIcon',
    bgColor: 'bg-warning-500',
  },
  {
    name: '排名',
    path: '/student/rank',
    icon: 'TrophyIcon',
    bgColor: 'bg-purple-500',
  },
];

const recentActivities = ref<any[]>([]);

// 获取成长值
const fetchGrowthScore = async () => {
  try {
    const response = await request.get('/api/v1/growth/score');
    if (response) {
      growthScore.value = {
        total_score: response.total_score,
        available_score: response.available_score,
      };
    }
  } catch (error) {
    console.error('获取成长值失败:', error);
  }
};

// 检查是否绑定班级
const checkBindClass = async () => {
  try {
    const response = await request.get('/api/v1/students/my-classes');
    console.log('绑定班级信息:', response);
    if (response && response.length > 0) {
      hasBindClass.value = true;
      // 保存所有绑定的班级信息
      bindClasses.value = response;
      // 保存第一个绑定班级信息（用于显示在顶部）
      bindClassInfo.value = response[0];
    } else {
      hasBindClass.value = false;
      bindClasses.value = [];
      bindClassInfo.value = null;
    }
  } catch (error) {
    console.error('检查绑定班级失败:', error);
    hasBindClass.value = false;
    bindClasses.value = [];
    bindClassInfo.value = null;
  }
};

// 获取最近兑换记录
const fetchRecentOrders = async () => {
  try {
    const response = await request.get('/api/v1/order/my-orders');
    if (response && response.items) {
      // 只取最近3条
      recentOrders.value = response.items.slice(0, 3);
    }
  } catch (error) {
    console.error('获取最近兑换记录失败:', error);
  }
};

// 获取最新动态
const fetchRecentActivities = async () => {
  try {
    const response = await request.get('/api/v1/growth/logs?identity=student');
    if (response && response.items) {
      // 只取最近5条
      const logs = response.items.slice(0, 5);
      // 转换为最新动态格式
      recentActivities.value = logs.map((log: any) => {
        let title = log.reason || '成长值变动';
        let icon = 'StarIcon';
        let iconBg = 'bg-success-500';
        
        if (log.change_score < 0) {
          iconBg = 'bg-danger-500';
        }
        
        // 计算时间差
        const now = new Date();
        const logTime = new Date(log.created_at);
        const diffMs = now.getTime() - logTime.getTime();
        const diffMinutes = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);
        
        let time = '';
        if (diffMinutes < 60) {
          time = `${diffMinutes}分钟前`;
        } else if (diffHours < 24) {
          time = `${diffHours}小时前`;
        } else if (diffDays < 30) {
          time = `${diffDays}天前`;
        } else {
          time = logTime.toLocaleDateString();
        }
        
        return {
          title,
          time,
          score: log.change_score,
          icon,
          iconBg,
        };
      });
    }
  } catch (error) {
    console.error('获取最新动态失败:', error);
  }
};

// 打开扫码器
const openScanner = async () => {
  showScanner.value = true;

  // 等待DOM更新后初始化扫码器
  setTimeout(async () => {
    try {
      // 停止之前可能存在的扫码器
      if (html5Qrcode) {
        await html5Qrcode.stop();
        html5Qrcode = null;
      }

      // 初始化扫码器
      html5Qrcode = new Html5Qrcode('qr-code-scanner');

      // 开始扫码
      await html5Qrcode.start(
        {
          facingMode: 'environment',
        },
        {
          fps: 10,
          qrbox: { width: 250, height: 250 },
        },
        (decodedText) => {
          // 处理扫码结果
          handleScanResult(decodedText);
        },
        (errorMessage) => {
          // 处理错误，这里可以忽略，因为扫码过程中会有很多错误
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

// 打开手动绑定弹窗
const openManualBind = () => {
  showManualBind.value = true;
};

// 在手动绑定弹窗中打开扫码器
const openScannerInManualBind = async () => {
  // 关闭手动绑定弹窗
  showManualBind.value = false;
  // 设置标记，表示扫码后需要重新打开手动绑定弹窗
  scannerFromManualBind.value = true;
  // 打开扫码器
  await openScanner();
};

// 关闭手动绑定弹窗
const closeManualBind = () => {
  showManualBind.value = false;
  manualClassId.value = '';
  manualNameInClass.value = '';
  manualStudentNoInClass.value = '';
};

// 提交手动绑定
const submitManualBind = async () => {
  if (!manualClassId.value) {
    alert('请输入班级二维码内容');
    return;
  }
  if (!manualNameInClass.value) {
    alert('请输入班级内姓名');
    return;
  }
  if (!manualStudentNoInClass.value) {
    alert('请输入班级内学号');
    return;
  }

  // 解析二维码内容
  let qrCode = '';
  if (manualClassId.value.startsWith('class:')) {
    // 提取 qr_code
    qrCode = manualClassId.value.substring(6);
  } else {
    // 直接使用输入作为 qr_code
    qrCode = manualClassId.value;
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
      name_in_class: manualNameInClass.value,
      student_no_in_class: manualStudentNoInClass.value,
    };

    const response = await request.post('/api/v1/students/bind', bindData);

    if (response.message === '绑定成功') {
      alert('绑定成功！');
      // 重新检查绑定状态
      await checkBindClass();
      if (hasBindClass.value) {
        await fetchGrowthScore();
      }
      closeManualBind();
    } else if (response.message === '绑定申请已提交，请等待导师审批') {
      alert('绑定申请已提交，请等待导师审批');
      closeManualBind();
    } else {
      alert('绑定失败：' + (response.message || '未知错误'));
    }
  } catch (error) {
    console.error('手动绑定失败:', error);
    alert('绑定失败，请稍后重试');
  }
};

// 切换班级
const switchClass = async (classId: number, studentId: number) => {
  try {
    await request.post(`/api/v1/class-student/${studentId}/switch-class`, {
      new_class_id: classId
    });
    alert('切换班级成功！');
    // 重新检查绑定状态
    await checkBindClass();
    if (hasBindClass.value) {
      await fetchGrowthScore();
    }
  } catch (error) {
    console.error('切换班级失败:', error);
    alert('切换班级失败，请稍后重试');
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
      // 提取 qr_code
      qrCode = result.substring(6);
    } else {
      // 尝试作为普通字符串处理
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
      // 如果来自手动绑定弹窗，提示后重新打开手动绑定弹窗
      if (scannerFromManualBind.value) {
        scannerFromManualBind.value = false;
        showManualBind.value = true;
      }
      return;
    }

    if (!classInfo || !classInfo.id) {
      alert('无效的班级二维码或班级不存在');
      // 如果来自手动绑定弹窗，提示后重新打开手动绑定弹窗
      if (scannerFromManualBind.value) {
        scannerFromManualBind.value = false;
        showManualBind.value = true;
      }
      return;
    }

    // 如果来自手动绑定弹窗，填充班级二维码内容并重新打开手动绑定弹窗
    if (scannerFromManualBind.value) {
      scannerFromManualBind.value = false;
      manualClassId.value = result; // 使用原始扫码结果（包括 class: 前缀）
      showManualBind.value = true;
      return;
    }

    // 获取班级内姓名和学号
    const nameInClass = prompt('请输入班级内姓名（老师给的名字）：');
    if (!nameInClass) {
      alert('姓名不能为空');
      return;
    }

    const studentNoInClass = prompt('请输入班级内学号（老师给的学号）：');
    if (!studentNoInClass) {
      alert('学号不能为空');
      return;
    }

    // 调用绑定接口
    const bindData = {
      qr_code: qrCode,
      name_in_class: nameInClass,
      student_no_in_class: studentNoInClass,
    };

    const response = await request.post('/api/v1/students/bind', bindData);

    if (response.message === '绑定成功') {
      alert('绑定成功！');
      // 重新检查绑定状态
      await checkBindClass();
      if (hasBindClass.value) {
        await fetchGrowthScore();
      }
    } else if (response.message === '绑定申请已提交，请等待导师审批') {
      alert('绑定申请已提交，请等待导师审批');
    } else {
      alert('绑定失败：' + (response.message || '未知错误'));
    }
  } catch (error) {
    console.error('处理扫码结果失败:', error);
    alert('绑定失败，请稍后重试');
  }
};

onMounted(async () => {
  await checkBindClass();
  if (hasBindClass.value) {
    await fetchGrowthScore();
    await fetchRecentOrders();
    await fetchRecentActivities();
  }
  // 检查是否需要打开绑定弹窗（从助理端跳转过来的情况）
  if (sessionStorage.getItem('openBindModalFromAssistant') === 'true') {
    sessionStorage.removeItem('openBindModalFromAssistant');
    openManualBind();
  } else if (sessionStorage.getItem('openBindModal') === 'true') {
    sessionStorage.removeItem('openBindModal');
    openManualBind();
  }
});
</script>
