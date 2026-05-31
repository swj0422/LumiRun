<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-900">系统日志</h1>
      <div class="text-sm text-gray-500">
        日志只可查看，不可删除或修改
      </div>
    </div>

    <div class="flex gap-4 mb-4">
      <button
        @click="activeTab = 'user'"
        :class="activeTab === 'user' ? 'bg-primary-500 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'"
        class="px-6 py-2 rounded-lg text-sm font-medium shadow"
      >
        用户操作日志
      </button>
      <button
        @click="activeTab = 'student'"
        :class="activeTab === 'student' ? 'bg-primary-500 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'"
        class="px-6 py-2 rounded-lg text-sm font-medium shadow"
      >
        成员操作日志
      </button>
      <button
        @click="activeTab = 'growth'"
        :class="activeTab === 'growth' ? 'bg-primary-500 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'"
        class="px-6 py-2 rounded-lg text-sm font-medium shadow"
      >
        成长操作日志
      </button>
    </div>

    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作人</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">模块</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作内容</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">IP地址</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">时间</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="log in logs" :key="log.id">
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ log.real_name || log.username || '-' }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ log.module }}</td>
            <td class="px-6 py-4 text-sm text-gray-500">{{ log.action }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 font-mono text-xs">{{ log.ip_address || '-' }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ formatDate(log.created_at) }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
              <button @click="viewDetail(log)" class="text-blue-600 hover:text-blue-700">详情</button>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="logs.length === 0" class="text-center py-12">
        <p class="text-gray-500">暂无日志数据</p>
      </div>
    </div>

    <div v-if="showDetailModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl p-6 w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-bold">日志详情</h2>
          <button @click="showDetailModal = false" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="flex-1 overflow-y-auto space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div class="flex justify-between py-2 border-b border-gray-100">
              <span class="text-gray-500">操作人</span>
              <span class="font-medium">{{ selectedLog?.real_name || selectedLog?.username || '-' }}</span>
            </div>
            <div class="flex justify-between py-2 border-b border-gray-100">
              <span class="text-gray-500">模块</span>
              <span class="font-medium">{{ selectedLog?.module }}</span>
            </div>
            <div class="flex justify-between py-2 border-b border-gray-100">
              <span class="text-gray-500">操作内容</span>
              <span class="font-medium">{{ selectedLog?.action }}</span>
            </div>
            <div class="flex justify-between py-2 border-b border-gray-100">
              <span class="text-gray-500">IP地址</span>
              <span class="font-medium font-mono text-xs">{{ selectedLog?.ip_address || '-' }}</span>
            </div>
            <div class="flex justify-between py-2 border-b border-gray-100 col-span-2">
              <span class="text-gray-500">操作时间</span>
              <span class="font-medium">{{ formatDate(selectedLog?.created_at) }}</span>
            </div>
          </div>

          <div v-if="selectedLog?.before_data" class="mt-4">
            <h3 class="text-sm font-medium text-gray-700 mb-2">操作前数据</h3>
            <pre class="bg-gray-50 p-4 rounded-lg text-xs overflow-x-auto">{{ formatJson(selectedLog?.before_data) }}</pre>
          </div>

          <div v-if="selectedLog?.after_data" class="mt-4">
            <h3 class="text-sm font-medium text-gray-700 mb-2">操作后数据</h3>
            <pre class="bg-gray-50 p-4 rounded-lg text-xs overflow-x-auto">{{ formatJson(selectedLog?.after_data) }}</pre>
          </div>
        </div>
        <div class="mt-4 flex justify-end">
          <button @click="showDetailModal = false" class="btn-primary">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import request from '@/api/request';
import { onMounted, ref, watch } from 'vue';

interface Log {
  id: number;
  username: string;
  real_name: string;
  log_type: string;
  module: string;
  action: string;
  ip_address: string;
  before_data: string;
  after_data: string;
  created_at: string;
}

const activeTab = ref<'user' | 'student' | 'growth'>('user');
const logs = ref<Log[]>([]);
const showDetailModal = ref(false);
const selectedLog = ref<Log | null>(null);

const fetchLogs = async () => {
  try {
    const endpoint = `/api/v1/system-logs/type/${activeTab.value}`;
    const data = (await request.get(endpoint)) as { items: Log[] };
    logs.value = data.items || [];
  } catch (error) {
    console.error('获取日志失败:', error);
    logs.value = [];
  }
};

const viewDetail = (log: Log) => {
  selectedLog.value = log;
  showDetailModal.value = true;
};

const formatDate = (date: string | undefined) => {
  if (!date) return '-';
  return new Date(date).toLocaleString('zh-CN');
};

const formatJson = (data: string | undefined) => {
  if (!data) return '-';
  try {
    return JSON.stringify(JSON.parse(data), null, 2);
  } catch {
    return data;
  }
};

watch(activeTab, () => {
  fetchLogs();
});

onMounted(() => {
  fetchLogs();
});
</script>
