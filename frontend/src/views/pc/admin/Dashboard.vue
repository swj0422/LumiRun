<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold text-gray-900">管理后台</h1>
      <div class="text-sm text-gray-500">
        {{ currentDate }}
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div
            class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center"
          >
            <svg
              class="w-6 h-6 text-blue-600"
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
            <p class="text-sm font-medium text-gray-500">用户总数</p>
            <p class="text-2xl font-bold text-gray-900">
              {{ stats.userCount }}
            </p>
          </div>
        </div>
        <div class="mt-3 text-xs text-gray-400">
          管理者: {{ stats.teacherCount }} | 成员: {{ stats.studentCount }}
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div
            class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center"
          >
            <svg
              class="w-6 h-6 text-green-600"
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
            <p class="text-sm font-medium text-gray-500">组织总数</p>
            <p class="text-2xl font-bold text-gray-900">
              {{ stats.classCount }}
            </p>
          </div>
        </div>
        <div class="mt-3 text-xs text-gray-400">
          今日新增: {{ stats.todayNewClassCount }}
        </div>
      </div>

      <div
        class="bg-white rounded-lg shadow p-6 cursor-pointer hover:shadow-md transition-shadow"
        @click="goToPendingTeachers"
      >
        <div class="flex items-center">
          <div
            class="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center"
          >
            <svg
              class="w-6 h-6 text-yellow-600"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">待审核管理者</p>
            <p class="text-2xl font-bold text-gray-900">
              {{ stats.pendingTeacherCount }}
            </p>
          </div>
        </div>
        <p class="text-xs text-gray-400 mt-2">点击查看详情</p>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
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
            <p class="text-sm font-medium text-gray-500">待处理订单</p>
            <p class="text-2xl font-bold text-gray-900">
              {{ stats.pendingOrderCount }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">今日统计</h2>
        <div class="space-y-4">
          <div class="flex justify-between items-center py-2 border-b border-gray-100">
            <span class="text-sm text-gray-600">新增组织</span>
            <span class="text-lg font-semibold text-blue-600">{{ stats.todayNewClassCount }}</span>
          </div>
          <div class="flex justify-between items-center py-2 border-b border-gray-100">
            <span class="text-sm text-gray-600">成长操作次数</span>
            <span class="text-lg font-semibold text-green-600">{{ stats.todayGrowthCount }}</span>
          </div>
          <div class="flex justify-between items-center py-2">
            <span class="text-sm text-gray-600">兑换订单数</span>
            <span class="text-lg font-semibold text-purple-600">{{ stats.todayOrderCount }}</span>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-lg font-semibold text-gray-900">待审核管理者</h2>
          <router-link
            v-if="pendingTeachers.length > 0"
            to="/admin/users?role_id=3&status=false"
            class="text-sm text-primary-600 hover:text-primary-700"
          >
            查看全部
          </router-link>
        </div>
        <div class="space-y-4 max-h-64 overflow-y-auto">
          <div
            v-if="pendingTeachers.length === 0"
            class="text-center py-4 text-gray-500"
          >
            暂无待审核管理者
          </div>
          <div
            v-for="teacher in pendingTeachers"
            :key="teacher.id"
            class="flex items-center justify-between py-3 border-b border-gray-100 last:border-0"
          >
            <div>
              <p class="text-sm font-medium text-gray-900">
                {{ teacher.real_name }}
              </p>
              <p class="text-xs text-gray-500">{{ teacher.email }}</p>
            </div>
            <div class="space-x-2">
              <button
                @click="approveTeacher(teacher.id)"
                class="px-3 py-1 text-sm bg-green-100 text-green-700 rounded hover:bg-green-200"
              >
                通过
              </button>
              <button
                @click="rejectTeacher(teacher.id)"
                class="px-3 py-1 text-sm bg-red-100 text-red-700 rounded hover:bg-red-200"
              >
                拒绝
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-lg font-semibold text-gray-900">最近操作日志</h2>
          <router-link
            to="/admin/logs"
            class="text-sm text-primary-600 hover:text-primary-700"
          >
            查看全部
          </router-link>
        </div>
        <div class="space-y-3 max-h-64 overflow-y-auto">
          <div
            v-if="recentLogs.length === 0"
            class="text-center py-4 text-gray-500"
          >
            暂无操作日志
          </div>
          <div
            v-for="log in recentLogs"
            :key="log.id"
            class="py-2 border-b border-gray-100 last:border-0"
          >
            <div class="flex justify-between items-start">
              <div class="flex-1">
                <p class="text-sm font-medium text-gray-900">{{ log.action }}</p>
                <p class="text-xs text-gray-500">{{ log.module }} | {{ log.real_name || log.username }}</p>
              </div>
              <span class="text-xs text-gray-400">{{ formatTime(log.created_at) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import request from '@/api/request';
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

const currentDate = computed(() => {
  return new Date().toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long',
  });
});

const stats = ref({
  userCount: 0,
  classCount: 0,
  teacherCount: 0,
  studentCount: 0,
  pendingTeacherCount: 0,
  pendingOrderCount: 0,
  todayNewClassCount: 0,
  todayGrowthCount: 0,
  todayOrderCount: 0,
});

const pendingTeachers = ref<any[]>([]);
const recentLogs = ref<any[]>([]);

const fetchStats = async () => {
  try {
    const data = (await request.get('/api/v1/admin/stats')) as any;
    stats.value = data;
  } catch (error) {
    console.error('获取统计数据失败:', error);
  }
};

const fetchPendingTeachers = async () => {
  try {
    const data = (await request.get('/api/v1/admin/users', {
      params: {
        role_id: 3,
        status: false,
      },
    })) as { items: any[] };
    pendingTeachers.value = data.items || [];
  } catch (error) {
    console.error('获取待审核管理者失败:', error);
  }
};

const fetchRecentLogs = async () => {
  try {
    const data = (await request.get('/api/v1/admin/recent-logs?limit=10')) as any[];
    recentLogs.value = data || [];
  } catch (error) {
    console.error('获取最近日志失败:', error);
  }
};

const goToPendingTeachers = () => {
  router.push('/admin/users?role_id=3&status=false');
};

const approveTeacher = async (id: number) => {
  try {
    await request.post(`/api/v1/admin/users/${id}/approve`);
    fetchPendingTeachers();
    fetchStats();
  } catch (error) {
    console.error('审核失败:', error);
  }
};

const rejectTeacher = async (id: number) => {
  try {
    await request.post(`/api/v1/admin/users/${id}/reject`);
    fetchPendingTeachers();
    fetchStats();
  } catch (error) {
    console.error('拒绝失败:', error);
  }
};

const formatTime = (time: string) => {
  if (!time) return '';
  const date = new Date(time);
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  
  if (minutes < 1) return '刚刚';
  if (minutes < 60) return `${minutes}分钟前`;
  if (hours < 24) return `${hours}小时前`;
  return date.toLocaleDateString('zh-CN');
};

onMounted(() => {
  fetchStats();
  fetchPendingTeachers();
  fetchRecentLogs();
});
</script>
