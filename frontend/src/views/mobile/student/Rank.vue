<template>
  <div class="space-y-6">
    <div class="bg-white shadow rounded-lg p-6">
      <h1 class="text-2xl font-bold text-gray-900 mb-6">组织排名</h1>
      
      <!-- 组织切换 -->
      <div v-if="bindClasses.length > 1" class="mb-6">
        <h2 class="text-lg font-semibold text-gray-800 mb-4">选择组织</h2>
        <div class="flex flex-wrap gap-2">
          <button 
            v-for="cls in bindClasses"
            :key="cls.id"
            @click="selectClass(cls.class_id)"
            :class="{
              'px-4 py-2 rounded-md text-sm font-medium': true,
              'bg-primary-100 text-primary-800': selectedClassId === cls.class_id,
              'bg-gray-100 text-gray-800': selectedClassId !== cls.class_id
            }"
          >
            {{ cls.school_name }} {{ cls.session }}级 {{ cls.class_name }}班
          </button>
        </div>
      </div>

      <!-- 自己排名卡片 -->
      <div v-if="currentUserRank" class="mb-6 p-4 bg-primary-50 rounded-lg">
        <h2 class="text-lg font-semibold text-gray-800 mb-2">我的排名</h2>
        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <div class="w-12 h-12 flex items-center justify-center">
              <div v-if="currentUserRank.rank === 1" class="w-12 h-12 flex items-center justify-center">
                <svg class="w-8 h-8 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
              </div>
              <div v-else-if="currentUserRank.rank === 2" class="w-12 h-12 flex items-center justify-center">
                <svg class="w-8 h-8 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
              </div>
              <div v-else-if="currentUserRank.rank === 3" class="w-12 h-12 flex items-center justify-center">
                <svg class="w-8 h-8 text-amber-700" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
              </div>
              <div v-else class="w-12 h-12 rounded-full bg-primary-600 flex items-center justify-center text-white font-bold text-lg">
                {{ currentUserRank.rank }}
              </div>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-900">{{ currentUserRank.real_name }}</p>
              <p class="text-xs text-gray-500">学号: {{ currentUserRank.student_no_in_class || '-' }}</p>
            </div>
          </div>
          <div class="text-right">
            <p class="text-lg font-bold text-primary-800">{{ currentUserRank.total_score }}</p>
            <p class="text-xs text-gray-500">总成长值</p>
          </div>
        </div>
      </div>
      
      <div class="mb-4">
        <h2 class="text-lg font-semibold text-gray-800 mb-4">成长值排行榜</h2>
        <div class="space-y-3">
          <div v-for="(student, index) in rankList" :key="index" class="flex items-center p-3 rounded-lg" :class="[student.is_current_user ? 'bg-primary-50' : 'bg-gray-50', index < 3 ? 'bg-yellow-50' : '']">
            <div class="w-8 h-8 flex items-center justify-center">
              <div v-if="index === 0" class="w-8 h-8 flex items-center justify-center">
                <svg class="w-6 h-6 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
              </div>
              <div v-else-if="index === 1" class="w-8 h-8 flex items-center justify-center">
                <svg class="w-6 h-6 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
              </div>
              <div v-else-if="index === 2" class="w-8 h-8 flex items-center justify-center">
                <svg class="w-6 h-6 text-amber-700" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
              </div>
              <span v-else class="w-6 h-6 rounded-full flex items-center justify-center font-bold text-white text-xs bg-gray-400">
                {{ index + 1 }}
              </span>
            </div>
            <div class="ml-3 flex-1">
              <p class="text-sm font-medium text-gray-900">{{ student.real_name }}</p>
              <p class="text-xs text-gray-500">学号: {{ student.student_no_in_class || '-' }}</p>
            </div>
            <div class="text-right">
              <p class="text-sm font-semibold text-gray-900">{{ student.total_score }}</p>
              <p class="text-xs text-gray-500">总成长值</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import request from '@/api/request';
import { onMounted, ref, computed } from 'vue';

const rankList = ref<any[]>([]);
const bindClasses = ref<any[]>([]);
const selectedClassId = ref<number | null>(null);

// 计算属性：当前用户的排名信息
const currentUserRank = computed(() => {
  const currentUser = rankList.value.find(student => student.is_current_user);
  if (currentUser) {
    const rank = rankList.value.findIndex(student => student.is_current_user) + 1;
    return {
      ...currentUser,
      rank
    };
  }
  return null;
});

// 获取绑定的组织列表
const fetchBindClasses = async () => {
  try {
    const response = await request.get('/api/v1/students/my-classes');
    if (response && response.length > 0) {
      bindClasses.value = response;
      // 默认选择第一个组织
      if (!selectedClassId.value && response[0] && response[0].class_id) {
        selectedClassId.value = response[0].class_id;
      }
    }
  } catch (error) {
    console.error('获取绑定组织失败:', error);
  }
};

// 获取组织排名
const fetchRankList = async () => {
  try {
    if (!selectedClassId.value || selectedClassId.value === undefined || selectedClassId.value === null) {
      return;
    }
    const response = await request.get('/api/v1/growth/leaderboard/class/' + selectedClassId.value);
    if (response && response.items) {
      rankList.value = response.items;
    }
  } catch (error) {
    console.error('获取排名失败:', error);
  }
};

// 选择组织
const selectClass = async (classId: number) => {
  selectedClassId.value = classId;
  await fetchRankList();
};

onMounted(async () => {
  await fetchBindClasses();
  await fetchRankList();
});
</script>