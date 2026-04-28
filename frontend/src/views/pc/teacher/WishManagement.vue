<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 顶部标题 -->
    <div class="bg-white shadow-sm">
      <div class="max-w-6xl mx-auto px-6 py-4">
        <div class="flex items-center justify-between">
          <h1 class="text-xl font-semibold text-gray-800">心愿墙管理</h1>
        </div>
      </div>
    </div>

    <div class="max-w-6xl mx-auto px-6 py-6">
      <!-- 筛选栏 -->
      <div class="bg-white rounded-lg shadow-sm p-4 mb-6">
        <div class="flex flex-wrap gap-4 items-center">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">选择班级</label>
            <select
              v-model="filterForm.class_id"
              class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">全部班级</option>
              <option v-for="cls in classes" :key="cls.id" :value="cls.id">
                {{ cls.school_name }} {{ cls.session }}级 {{ cls.class_name }}班
              </option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">状态</label>
            <select
              v-model="filterForm.status"
              class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">全部状态</option>
              <option :value="0">待处理</option>
              <option :value="1">已实现</option>
              <option :value="2">已拒绝</option>
            </select>
          </div>
          <div class="flex items-center gap-2 pt-5">
            <button @click="fetchWishes" class="btn-primary px-4 py-2">
              查询
            </button>
            <button @click="resetFilter" class="btn-secondary px-4 py-2">
              重置
            </button>
          </div>
        </div>
      </div>

      <!-- 统计卡片 -->
      <div class="grid grid-cols-3 gap-4 mb-6">
        <div class="bg-white rounded-lg shadow-sm p-4">
          <p class="text-gray-500 text-sm">总心愿数</p>
          <p class="text-2xl font-bold text-gray-800">{{ stats.total }}</p>
        </div>
        <div class="bg-primary-50 rounded-lg shadow-sm p-4">
          <p class="text-primary-600 text-sm">待处理</p>
          <p class="text-2xl font-bold text-primary-800">{{ stats.pending }}</p>
        </div>
        <div class="bg-success-50 rounded-lg shadow-sm p-4">
          <p class="text-success-600 text-sm">已实现</p>
          <p class="text-2xl font-bold text-success-800">{{ stats.completed }}</p>
        </div>
      </div>

      <!-- 心愿列表 -->
      <div class="bg-white rounded-lg shadow-sm">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr class="bg-gray-50">
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">学员</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">班级</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">心愿标题</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">图片</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">创建时间</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200">
              <tr v-for="wish in wishes" :key="wish.id">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-800">{{ wish.user_name }}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-800">{{ wish.class_name }}</div>
                </td>
                <td class="px-6 py-4">
                  <div class="text-sm text-gray-800">{{ wish.title }}</div>
                  <div v-if="wish.description" class="text-xs text-gray-500 mt-1 line-clamp-2">{{ wish.description }}</div>
                </td>
                <td class="px-6 py-4">
                  <div v-if="wish.image_urls && wish.image_urls.length > 0" class="flex space-x-2">
                    <img
                      v-for="(img, idx) in wish.image_urls.slice(0, 3)"
                      :key="idx"
                      :src="img"
                      class="w-12 h-12 rounded-lg object-cover cursor-pointer"
                      @click="previewImage(img)"
                    />
                  </div>
                  <span v-else class="text-xs text-gray-400">无图片</span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span
                    :class="{
                      'px-2 py-1 rounded-full text-xs font-medium': true,
                      'bg-primary-100 text-primary-800': wish.status === 0,
                      'bg-success-100 text-success-800': wish.status === 1,
                      'bg-gray-100 text-gray-800': wish.status === 2
                    }"
                  >
                    {{ ["待处理", "已实现", "已拒绝"][wish.status] }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ formatDate(wish.created_at) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex space-x-2">
                    <button
                      @click="viewWish(wish)"
                      class="text-primary-600 hover:text-primary-800 text-sm"
                    >
                      查看
                    </button>
                    <button
                      v-if="wish.status === 0"
                      @click="processWish(wish)"
                      class="text-success-600 hover:text-success-800 text-sm"
                    >
                      处理
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 分页 -->
        <div class="px-6 py-4 border-t border-gray-200 flex justify-between items-center">
          <p class="text-sm text-gray-500">共 {{ total }} 条记录</p>
          <div class="flex space-x-2">
            <button
              @click="prevPage"
              :disabled="currentPage === 1"
              class="px-3 py-1 border border-gray-300 rounded-md text-sm"
              :class="{ 'opacity-50 cursor-not-allowed': currentPage === 1 }"
            >
              上一页
            </button>
            <span class="px-3 py-1 text-sm">{{ currentPage }} / {{ totalPages }}</span>
            <button
              @click="nextPage"
              :disabled="currentPage === totalPages"
              class="px-3 py-1 border border-gray-300 rounded-md text-sm"
              :class="{ 'opacity-50 cursor-not-allowed': currentPage === totalPages }"
            >
              下一页
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 查看详情弹窗 -->
    <div
      v-if="showDetailModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg p-6 max-w-lg w-full mx-4 max-h-[80vh] overflow-y-auto">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold">心愿详情</h3>
          <button @click="closeDetailModal" class="text-gray-500 hover:text-gray-700">
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <div v-if="currentWish" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">学员</label>
            <p class="text-gray-800">{{ currentWish.user_name }}</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">班级</label>
            <p class="text-gray-800">{{ currentWish.class_name }}</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">心愿标题</label>
            <p class="text-gray-800">{{ currentWish.title }}</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">心愿描述</label>
            <p class="text-gray-800">{{ currentWish.description || '无' }}</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">图片</label>
            <div v-if="currentWish.image_urls && currentWish.image_urls.length > 0" class="flex flex-wrap gap-2">
              <img
                v-for="(img, idx) in currentWish.image_urls"
                :key="idx"
                :src="img"
                class="w-24 h-24 rounded-lg object-cover"
              />
            </div>
            <p v-else class="text-gray-400">无图片</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">状态</label>
            <p :class="{
              'text-primary-600': currentWish.status === 0,
              'text-success-600': currentWish.status === 1,
              'text-gray-600': currentWish.status === 2
            }">
              {{ ["待处理", "已实现", "已拒绝"][currentWish.status] }}
            </p>
          </div>
          <div v-if="currentWish.teacher_comment">
            <label class="block text-sm font-medium text-gray-700">导师回复</label>
            <p class="text-gray-800">{{ currentWish.teacher_comment }}</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">创建时间</label>
            <p class="text-gray-800">{{ formatDate(currentWish.created_at) }}</p>
          </div>
          
          <div v-if="currentWish.status === 0" class="flex space-x-2 pt-4">
            <button @click="showProcessModal = true" class="flex-1 btn-primary py-2">
              处理心愿
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 处理心愿弹窗 -->
    <div
      v-if="showProcessModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold">处理心愿</h3>
          <button @click="showProcessModal = false" class="text-gray-500 hover:text-gray-700">
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">处理结果</label>
            <div class="flex space-x-4">
              <label class="flex items-center">
                <input
                  v-model="processForm.status"
                  type="radio"
                  :value="1"
                  class="w-4 h-4 text-primary-600"
                />
                <span class="ml-2 text-sm text-gray-700">已实现</span>
              </label>
              <label class="flex items-center">
                <input
                  v-model="processForm.status"
                  type="radio"
                  :value="2"
                  class="w-4 h-4 text-primary-600"
                />
                <span class="ml-2 text-sm text-gray-700">已拒绝</span>
              </label>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">导师回复（可选）</label>
            <textarea
              v-model="processForm.comment"
              placeholder="输入回复内容..."
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            ></textarea>
          </div>
        </div>
        
        <div class="flex space-x-2 mt-6">
          <button @click="showProcessModal = false" class="flex-1 btn-secondary py-2">
            取消
          </button>
          <button @click="submitProcess" class="flex-1 btn-primary py-2">
            确认处理
          </button>
        </div>
      </div>
    </div>

    <!-- 图片预览弹窗 -->
    <div
      v-if="previewImageSrc"
      class="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50"
      @click="previewImageSrc = ''"
    >
      <img :src="previewImageSrc" class="max-w-full max-h-full object-contain" />
    </div>
  </div>
</template>

<script setup lang="ts">
import request from '@/api/request';
import { ref, onMounted, computed } from 'vue';

const wishes = ref<any[]>([]);
const classes = ref<any[]>([]);
const currentPage = ref(1);
const total = ref(0);
const pageSize = 20;

const filterForm = ref({
  class_id: '',
  status: ''
});

const stats = ref({
  total: 0,
  pending: 0,
  completed: 0
});

const showDetailModal = ref(false);
const showProcessModal = ref(false);
const currentWish = ref<any>(null);
const previewImageSrc = ref('');

const processForm = ref({
  status: 1,
  comment: ''
});

const totalPages = computed(() => Math.ceil(total.value / pageSize));

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleString('zh-CN');
};

const fetchClasses = async () => {
  try {
    const response = await request.get('/api/v1/classes/my');
    if (response && response.items) {
      classes.value = response.items;
    }
  } catch (error) {
    console.error('获取班级列表失败:', error);
  }
};

const fetchWishes = async () => {
  try {
    const params: any = {
      skip: (currentPage.value - 1) * pageSize,
      limit: pageSize
    };
    if (filterForm.value.class_id) {
      params.class_id = filterForm.value.class_id;
    }
    if (filterForm.value.status !== '') {
      params.status = filterForm.value.status;
    }
    
    const response = await request.get('/api/v1/wishes/teacher', { params });
    if (response) {
      wishes.value = response.items;
      total.value = response.total;
      calculateStats();
    }
  } catch (error) {
    console.error('获取心愿列表失败:', error);
  }
};

const calculateStats = () => {
  stats.value = {
    total: total.value,
    pending: wishes.value.filter(w => w.status === 0).length,
    completed: wishes.value.filter(w => w.status === 1).length
  };
};

const resetFilter = () => {
  filterForm.value = {
    class_id: '',
    status: ''
  };
  currentPage.value = 1;
  fetchWishes();
};

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--;
    fetchWishes();
  }
};

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++;
    fetchWishes();
  }
};

const viewWish = (wish: any) => {
  currentWish.value = wish;
  showDetailModal.value = true;
};

const closeDetailModal = () => {
  showDetailModal.value = false;
  currentWish.value = null;
};

const processWish = (wish: any) => {
  currentWish.value = wish;
  showDetailModal.value = false;
  showProcessModal.value = true;
  processForm.value = {
    status: 1,
    comment: ''
  };
};

const submitProcess = async () => {
  if (!currentWish.value) return;

  try {
    await request.post(`/api/v1/wishes/${currentWish.value.id}/process`, {
      status: processForm.value.status,
      teacher_comment: processForm.value.comment
    });
    
    showProcessModal.value = false;
    currentWish.value = null;
    fetchWishes();
    alert('处理成功');
  } catch (error) {
    console.error('处理心愿失败:', error);
    alert('处理失败，请稍后重试');
  }
};

const previewImage = (src: string) => {
  previewImageSrc.value = src;
};

onMounted(async () => {
  await fetchClasses();
  await fetchWishes();
});
</script>