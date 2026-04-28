<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-900">系统日志</h1>
    </div>

    <div class="bg-white rounded-lg shadow p-4">
      <div class="flex flex-wrap gap-4">
        <select v-model="logType" class="input w-40" @change="fetchLogs">
          <option value="system">系统日志</option>
          <option value="operation">操作日志</option>
        </select>
        <select v-model="logLevel" class="input w-32" @change="fetchLogs">
          <option value="">全部级别</option>
          <option value="INFO">INFO</option>
          <option value="WARNING">WARNING</option>
          <option value="ERROR">ERROR</option>
        </select>
      </div>
    </div>

    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <template v-if="logType === 'system'">
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                时间
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                级别
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                模块
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                消息
              </th>
            </template>
            <template v-else>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                时间
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                操作人
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                操作
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                目标
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                IP
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                详情
              </th>
            </template>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <template v-if="logType === 'system'">
            <tr v-for="log in logs" :key="log.timestamp">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatTime(log.timestamp) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="getLevelClass(log.level)"
                  class="px-2 py-1 text-xs rounded-full"
                >
                  {{ log.level }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ log.module }}
              </td>
              <td class="px-6 py-4 text-sm text-gray-500">
                {{ log.message }}
              </td>
            </tr>
          </template>
          <template v-else>
            <tr v-for="log in logs" :key="log.id">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatTime(log.created_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ log.user_name }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ log.action }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ log.target }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ log.ip }}
              </td>
              <td class="px-6 py-4 text-sm text-gray-500">
                {{ log.details }}
              </td>
            </tr>
          </template>
        </tbody>
      </table>

      <div v-if="logs.length === 0" class="text-center py-12">
        <p class="text-gray-500">暂无日志数据</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import request from '@/api/request';
import { onMounted, ref, watch } from 'vue';

const logType = ref('system');
const logLevel = ref('');
const logs = ref<any[]>([]);

const fetchLogs = async () => {
  try {
    const params: Record<string, any> = {};
    if (logLevel.value) {
      params.level = logLevel.value;
    }

    const endpoint =
      logType.value === 'system' ? '/v1/logs/system' : '/v1/logs/operation';
    const data = (await request.get(endpoint, { params })) as { items: any[] };
    logs.value = data.items || [];
  } catch (error) {
    console.error('获取日志失败:', error);
    logs.value = [];
  }
};

const getLevelClass = (level: string) => {
  const classes: Record<string, string> = {
    INFO: 'bg-blue-100 text-blue-800',
    WARNING: 'bg-yellow-100 text-yellow-800',
    ERROR: 'bg-red-100 text-red-800',
  };
  return classes[level] || 'bg-gray-100 text-gray-800';
};

const formatTime = (time: string) => {
  return new Date(time).toLocaleString('zh-CN');
};

watch(logType, () => {
  logLevel.value = '';
  fetchLogs();
});

onMounted(() => {
  fetchLogs();
});
</script>
