<template>
  <div class="space-y-6">
    <div class="bg-white shadow rounded-lg p-6">
      <h1 class="text-2xl font-bold text-gray-900 mb-6">成长值明细</h1>
      
      <div class="grid grid-cols-2 gap-4 mb-6">
        <div class="bg-primary-50 rounded-lg p-4">
          <p class="text-sm text-primary-600">可用成长值</p>
          <p class="text-2xl font-bold text-primary-800">{{ growthScore.available_score }}</p>
          <button 
            @click="goToShop"
            class="mt-2 px-4 py-1 bg-primary-600 text-white text-sm rounded-md hover:bg-primary-700 transition-colors"
          >
            兑换奖励
          </button>
        </div>
        <div class="bg-gray-50 rounded-lg p-4">
          <p class="text-sm text-gray-600">累计成长值</p>
          <p class="text-2xl font-bold text-gray-800">{{ growthScore.total_score }}</p>
        </div>
      </div>

      <!-- 筛选栏 -->
      <div class="mb-6 bg-gray-50 p-4 rounded-lg">
        <div class="flex flex-wrap gap-4 mb-4">
          <div class="flex items-center">
            <label class="text-sm text-gray-600 mr-2">时间范围:</label>
            <select 
              v-model="selectedPeriod" 
              class="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option v-for="period in timePeriods" :key="period.value" :value="period.value">
                {{ period.label }}
              </option>
            </select>
          </div>
          <div class="flex items-center">
            <label class="text-sm text-gray-600 mr-2">类型:</label>
            <select 
              v-model="selectedType" 
              class="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option v-for="type in scoreTypes" :key="type.value" :value="type.value">
                {{ type.label }}
              </option>
            </select>
          </div>
        </div>
      </div>

      <div class="mb-4">
        <h2 class="text-lg font-semibold text-gray-800 mb-4">成长值变动记录</h2>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  变动值
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  原因
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  操作人
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  创建时间
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="(item, index) in filteredGrowthLogs" :key="index">
                <td class="px-6 py-4 whitespace-nowrap">
                  <span :class="item.change_score > 0 ? 'text-success-600' : 'text-danger-600'" class="font-semibold">
                    {{ item.change_score > 0 ? '+' : '' }}{{ item.change_score }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ item.reason }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ item.operator_name || '系统' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ new Date(item.created_at).toLocaleString() }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import request from '@/api/request';
import { onMounted, ref, computed } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

const growthScore = ref({
  total_score: 0,
  available_score: 0,
});

const growthLogs = ref<any[]>([]);
const selectedPeriod = ref('all');
const selectedType = ref('all');

// 时间范围选项
const timePeriods = [
  { label: '全部', value: 'all' },
  { label: '今日', value: 'today' },
  { label: '本周', value: 'week' },
  { label: '本月', value: 'month' },
  { label: '自定义', value: 'custom' },
];

// 类型选项
const scoreTypes = [
  { label: '全部', value: 'all' },
  { label: '加分', value: 'positive' },
  { label: '减分', value: 'negative' },
];



// 计算属性：筛选后的成长值记录
const filteredGrowthLogs = computed(() => {
  let filtered = [...growthLogs.value];
  
  // 按时间范围筛选
  if (selectedPeriod.value !== 'all') {
    const now = new Date();
    const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    
    filtered = filtered.filter(log => {
      const logDate = new Date(log.created_at);
      
      if (selectedPeriod.value === 'today') {
        return logDate >= todayStart;
      } else if (selectedPeriod.value === 'week') {
        const weekStart = new Date(todayStart);
        weekStart.setDate(todayStart.getDate() - 7);
        return logDate >= weekStart;
      } else if (selectedPeriod.value === 'month') {
        const monthStart = new Date(now.getFullYear(), now.getMonth(), 1);
        return logDate >= monthStart;
      }
      return true;
    });
  }
  
  // 按类型筛选
  if (selectedType.value !== 'all') {
    if (selectedType.value === 'positive') {
      filtered = filtered.filter(log => log.change_score > 0);
    } else if (selectedType.value === 'negative') {
      filtered = filtered.filter(log => log.change_score < 0);
    }
  }
  
  return filtered;
});

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

const fetchGrowthLogs = async () => {
  try {
    const response = await request.get('/api/v1/growth/logs?identity=student');
    if (response && response.items) {
      growthLogs.value = response.items;
    }
  } catch (error) {
    console.error('获取成长值记录失败:', error);
  }
};

const selectTimePeriod = (period: string) => {
  selectedPeriod.value = period;
  if (period === 'custom') {
    // 这里可以添加自定义时间范围的逻辑
    alert('自定义时间范围功能开发中');
    selectedPeriod.value = 'all';
  }
};

const selectScoreType = (type: string) => {
  selectedType.value = type;
};

const goToShop = () => {
  router.push('/student/shop');
};

onMounted(async () => {
  await fetchGrowthScore();
  await fetchGrowthLogs();
});
</script>