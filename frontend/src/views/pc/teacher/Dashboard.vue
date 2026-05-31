<template>
  <div class="space-y-6">
    <!-- 工作台 -->
    <div class="space-y-6">
      <!-- 页面标题 -->
      <div class="flex items-center justify-between">
        <div></div>
        <div class="text-sm text-gray-500">
          {{ currentDate }}
        </div>
      </div>

      <!-- 统计卡片 -->
      <!-- 第一行：我的组织、成员总数、奖励总数 -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
        <router-link
          to="/teacher/classes"
          class="card p-6 hover:shadow-md transition-shadow"
        >
          <div class="flex items-center">
            <div
              class="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center"
            >
              <svg
                class="w-6 h-6 text-primary-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
                />
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">我的组织</p>
              <p class="text-2xl font-bold text-gray-900">
                {{ stats.classCount }}
              </p>
            </div>
          </div>
        </router-link>

        <router-link
          to="/teacher/students"
          class="card p-6 hover:shadow-md transition-shadow"
        >
          <div class="flex items-center">
            <div
              class="w-12 h-12 bg-success-100 rounded-lg flex items-center justify-center"
            >
              <svg
                class="w-6 h-6 text-success-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"
                />
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">成员总数</p>
              <p class="text-2xl font-bold text-gray-900">
                {{ stats.studentCount }}
              </p>
            </div>
          </div>
        </router-link>

        <div class="card p-6">
          <div class="flex items-center">
            <div
              class="w-12 h-12 bg-warning-100 rounded-lg flex items-center justify-center"
            >
              <svg
                class="w-6 h-6 text-warning-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 8v13m0-13V6a2 2 0 112 2h-2zm0 0V5.5A2.5 2.5 0 109.5 8H12zm-7 4h14M5 12a2 2 0 110-4h14a2 2 0 110 4M5 12v7a2 2 0 002 2h10a2 2 0 002-2v-7"
                />
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">奖励总数</p>
              <p class="text-2xl font-bold text-gray-900">
                {{ stats.giftCount }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- 第二行：订单处理、绑定待审核 -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
        <router-link
          v-if="stats.pendingOrderCount > 0"
          to="/teacher/orders"
          class="card p-6 cursor-pointer hover:shadow-md transition-shadow"
        >
          <div class="flex items-center">
            <div
              class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center"
            >
              <svg
                class="w-6 h-6 text-purple-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                />
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">订单处理</p>
              <p class="text-2xl font-bold text-gray-900">
                {{ stats.pendingOrderCount }}
              </p>
            </div>
          </div>
        </router-link>
        <div v-else class="card p-6">
          <div class="flex items-center">
            <div
              class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center"
            >
              <svg
                class="w-6 h-6 text-purple-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                />
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">订单处理</p>
              <p class="text-2xl font-bold text-gray-900">
                {{ stats.pendingOrderCount }}
              </p>
            </div>
          </div>
        </div>

        <div class="card p-6">
          <div class="flex items-center">
            <div
              class="w-12 h-12 bg-danger-100 rounded-lg flex items-center justify-center"
            >
              <svg
                class="w-6 h-6 text-danger-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"
                />
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">绑定待审核</p>
              <p class="text-2xl font-bold text-gray-900">
                {{ stats.pendingBindCount }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- 快捷操作 -->
      <div class="card p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">快捷操作</h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <router-link
            to="/teacher/classes?create=true"
            class="flex flex-col items-center p-4 border border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors"
          >
            <svg
              class="w-8 h-8 text-primary-600 mb-2"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 6v6m0 0v6m0-6h6m-6 0H6"
              />
            </svg>
            <span class="text-sm font-medium">创建组织</span>
          </router-link>

          <router-link
            to="/teacher/growth?showRecord=true"
            class="flex flex-col items-center p-4 border border-gray-200 rounded-lg hover:border-success-500 hover:bg-success-50 transition-colors"
          >
            <svg
              class="w-8 h-8 text-success-600 mb-2"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 6v6m0 0v6m0-6h6m-6 0H6"
              />
            </svg>
            <span class="text-sm font-medium">录入成长值</span>
          </router-link>

          <router-link
            to="/teacher/rewards"
            class="flex flex-col items-center p-4 border border-gray-200 rounded-lg hover:border-warning-500 hover:bg-warning-50 transition-colors"
          >
            <svg
              class="w-8 h-8 text-warning-600 mb-2"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 6v6m0 0v6m0-6h6m-6 0H6"
              />
            </svg>
            <span class="text-sm font-medium">添加奖励</span>
          </router-link>

          <router-link
            to="/teacher/orders"
            class="flex flex-col items-center p-4 border border-gray-200 rounded-lg hover:border-purple-500 hover:bg-purple-50 transition-colors"
          >
            <svg
              class="w-8 h-8 text-purple-600 mb-2"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <span class="text-sm font-medium">核销订单</span>
          </router-link>
        </div>
      </div>

      <!-- 绑定待审核 -->
      <div v-if="pendingBinds.length > 0" class="card p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">绑定待审核 ({{ pendingBinds.length }})</h2>
        <div class="space-y-4">
          <div
            v-for="(item, index) in pendingBinds"
            :key="index"
            class="flex items-center justify-between py-3 border-b border-gray-100 last:border-0"
          >
            <div class="flex items-center">
              <div
                class="w-8 h-8 bg-warning-100 rounded-full flex items-center justify-center mr-3"
              >
                <svg
                  class="w-4 h-4 text-warning-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                  />
                </svg>
              </div>
              <div>
                <p class="text-sm font-medium text-gray-900">
                  {{ item.studentName }}
                </p>
                <p class="text-xs text-gray-500">
                  {{ item.className }} - 学号: {{ item.studentNo }}
                </p>
              </div>
            </div>
            <div class="flex items-center space-x-2">
              <span class="text-xs text-gray-400">{{ item.bindTime }}</span>
              <button
                @click="handleApproveBind(item.studentClassId)"
                class="px-3 py-1 bg-success-500 text-white text-xs rounded hover:bg-success-600"
              >
                同意
              </button>
              <button
                @click="handleRejectBind(item.studentClassId)"
                class="px-3 py-1 bg-danger-500 text-white text-xs rounded hover:bg-danger-600"
              >
                拒绝
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 最近动态 -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="card p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">成长值变动</h2>
          <div class="space-y-4">
            <div
              v-for="(item, index) in recentGrowthLogs"
              :key="index"
              class="flex items-center justify-between py-3 border-b border-gray-100 last:border-0"
            >
              <div class="flex items-center">
                <div
                  :class="`w-8 h-8 ${item.score > 0 ? 'bg-success-100' : 'bg-danger-100'} rounded-full flex items-center justify-center mr-3`"
                >
                  <span
                    :class="`text-sm font-bold ${item.score > 0 ? 'text-success-600' : 'text-danger-600'}`"
                  >
                    {{ item.score > 0 ? '+' : '' }}{{ item.score }}
                  </span>
                </div>
                <div>
                  <p class="text-sm font-medium text-gray-900">
                    {{ item.studentName }}
                  </p>
                  <p class="text-xs text-gray-500">{{ item.reason }}</p>
                </div>
              </div>
              <span class="text-xs text-gray-400">{{ item.time }}</span>
            </div>
          </div>
        </div>

        <div class="card p-6">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-lg font-semibold text-gray-900">订单处理</h2>
            <router-link
              to="/teacher/orders"
              class="text-sm text-blue-600 hover:text-blue-700"
            >
              查看全部
            </router-link>
          </div>
          <div class="space-y-4">
            <div
              v-for="(item, index) in pendingOrders"
              :key="index"
              class="flex items-center justify-between py-3 border-b border-gray-100 last:border-0"
            >
              <div class="flex items-center">
                <div
                  class="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center mr-3"
                >
                  <svg
                    class="w-4 h-4 text-primary-600"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"
                    />
                  </svg>
                </div>
                <div>
                  <p class="text-sm font-medium text-gray-900">
                    {{ item.studentName }}
                  </p>
                  <p class="text-xs text-gray-500">
                    兑换了 {{ item.giftName }}
                  </p>
                </div>
              </div>
              <span class="text-xs text-gray-400">{{ item.time }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import request from '@/api/request';
import dayjs from 'dayjs';
import { computed, onActivated, onMounted, ref } from 'vue';

const currentDate = computed(() => {
  return dayjs().format('YYYY年MM月DD日 dddd');
});

const stats = ref({
  classCount: 0,
  studentCount: 0,
  giftCount: 0,
  pendingOrderCount: 0,
  pendingBindCount: 0,
});

const recentGrowthLogs = ref<
  { studentName: string; score: number; reason: string; time: string }[]
>([]);

const pendingOrders = ref<
  { studentName: string; giftName: string; time: string }[]
>([]);

const pendingBinds = ref<
  { studentClassId: number; className: string; studentName: string; studentNo: string; bindTime: string }[]
>([]);

const fetchStats = async () => {
  try {
    const data = (await request.get('/api/v1/users/stats')) as {
      classCount: number;
      studentCount: number;
      giftCount: number;
      pendingOrderCount: number;
    };
    stats.value = {
      classCount: data.classCount || 0,
      studentCount: data.studentCount || 0,
      giftCount: data.giftCount || 0,
      pendingOrderCount: data.pendingOrderCount || 0,
      pendingBindCount: pendingBinds.value.length,
    };
  } catch (error) {
    console.error('获取统计数据失败:', error);
  }
};

const fetchRecentGrowthLogs = async () => {
  try {
    const response = (await request.get('/api/v1/growth/logs', {
      params: { limit: 5 },
    })) as { items: any[] };

    recentGrowthLogs.value = (response.items || []).map((item: any) => ({
      studentName: item.student_name || item.studentName || '未知',
      score: item.change_score || item.score || 0,
      reason: item.reason || '无原因',
      time: formatTime(item.created_at || item.createdAt),
    }));
  } catch (error) {
    console.error('获取成长值记录失败:', error);
  }
};

const fetchPendingOrders = async () => {
  try {
    const response = (await request.get('/api/v1/orders/teacher', {
      params: { status: 1, limit: 5 },
    })) as { items: any[] };

    pendingOrders.value = (response.items || []).map((item: any) => ({
      studentName: item.student_name || item.studentName || '未知',
      giftName: item.gift_name || item.giftName || '未知礼品',
      time: formatTime(item.created_at || item.createdAt),
    }));
  } catch (error) {
    console.error('获取待处理订单失败:', error);
  }
};

const fetchPendingBinds = async () => {
  try {
    const response = (await request.get('/api/v1/students/bind/pending')) as any[];
    pendingBinds.value = (response || []).map((item: any) => ({
      studentClassId: item.student_class_id,
      className: item.class_name,
      studentName: item.student_name,
      studentNo: item.student_no || '未填写',
      bindTime: formatTime(item.bind_time),
    }));
    stats.value.pendingBindCount = pendingBinds.value.length;
  } catch (error) {
    console.error('获取待审核绑定失败:', error);
  }
};

const handleApproveBind = async (studentClassId: number) => {
  try {
    await request.post(`/api/v1/students/bind/approve/${studentClassId}`);
    alert('已同意绑定申请');
    await fetchPendingBinds();
  } catch (error) {
    console.error('同意绑定失败:', error);
    alert('操作失败，请重试');
  }
};

const handleRejectBind = async (studentClassId: number) => {
  try {
    await request.post(`/api/v1/students/bind/reject/${studentClassId}`);
    alert('已拒绝绑定申请');
    await fetchPendingBinds();
  } catch (error) {
    console.error('拒绝绑定失败:', error);
    alert('操作失败，请重试');
  }
};

const formatTime = (dateStr: string) => {
  if (!dateStr) return '';
  // 直接解析ISO时间字符串（包含时区信息）
  const date = new Date(dateStr);
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);

  if (minutes < 1) return '刚刚';
  if (minutes < 60) return `${minutes}分钟前`;
  if (hours < 24) return `${hours}小时前`;
  return `${days}天前`;
};

onMounted(async () => {
  await Promise.all([
    fetchStats(),
    fetchRecentGrowthLogs(),
    fetchPendingOrders(),
    fetchPendingBinds(),
  ]);
});

onActivated(async () => {
  await Promise.all([
    fetchStats(),
    fetchRecentGrowthLogs(),
    fetchPendingOrders(),
    fetchPendingBinds(),
  ]);
});
</script>
