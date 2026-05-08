<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 页面标题 -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900">心愿便利贴管理</h1>
      <p class="mt-1 text-sm text-gray-500">管理平台上的所有心愿便利贴，可删除违规内容</p>
    </div>

    <!-- 搜索和筛选 -->
    <div class="bg-white rounded-xl shadow-sm p-4 mb-6">
      <div class="flex items-center justify-between">
        <div class="flex-1 max-w-md">
          <input
            v-model="searchKeyword"
            @keyup.enter="loadWishes"
            type="text"
            placeholder="搜索心愿内容..."
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
          />
        </div>
        <button
          @click="loadWishes"
          class="ml-4 px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
        >
          搜索
        </button>
      </div>
    </div>

    <!-- 统计信息 -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <div class="bg-white rounded-xl shadow-sm p-4">
        <div class="text-sm text-gray-500">总心愿数</div>
        <div class="text-2xl font-bold text-gray-900">{{ total }}</div>
      </div>
      <div class="bg-white rounded-xl shadow-sm p-4">
        <div class="text-sm text-gray-500">匿名心愿</div>
        <div class="text-2xl font-bold text-blue-600">{{ anonymousCount }}</div>
      </div>
      <div class="bg-white rounded-xl shadow-sm p-4">
        <div class="text-sm text-gray-500">带图心愿</div>
        <div class="text-2xl font-bold text-green-600">{{ imageCount }}</div>
      </div>
    </div>

    <!-- 心愿列表 -->
    <div class="bg-white rounded-xl shadow-sm overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                内容
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                发布者
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                是否匿名
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                图片
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                发布时间
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                操作
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="wish in wishList" :key="wish.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="max-w-xs truncate" :title="wish.content">{{ wish.content }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <button
                  v-if="!wish.is_anonymous"
                  @click="viewPublisher(wish)"
                  class="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded hover:bg-gray-200 transition-colors cursor-pointer"
                >
                  {{ wish.user_name }}
                </button>
                <span v-else class="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded">
                  匿名用户
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span v-if="wish.is_anonymous" class="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded">
                  是
                </span>
                <span v-else class="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-600 rounded">
                  否
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <button
                  v-if="wish.image_url"
                  @click="previewImage(wish.image_url)"
                  class="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded hover:bg-green-200 transition-colors cursor-pointer"
                >
                  查看图片
                </button>
                <span v-else class="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-400 rounded">
                  无
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(wish.created_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <button
                  @click="deleteWish(wish.id)"
                  class="px-3 py-1 text-xs font-medium text-red-600 bg-red-50 rounded hover:bg-red-100 transition-colors"
                >
                  删除
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 空状态 -->
      <div v-if="wishList.length === 0" class="py-12 text-center">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        <h3 class="mt-2 text-sm font-medium text-gray-900">暂无心愿便利贴</h3>
        <p class="mt-1 text-sm text-gray-500">平台上还没有心愿便利贴</p>
      </div>

      <!-- 分页 -->
      <div v-if="total > 0" class="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
        <div class="flex-1 flex justify-between sm:hidden">
          <button
            @click="prevPage"
            :disabled="currentPage === 1"
            class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            上一页
          </button>
          <button
            @click="nextPage"
            :disabled="currentPage >= totalPages"
            class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            下一页
          </button>
        </div>
        <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
          <div>
            <p class="text-sm text-gray-700">
              显示第 <span class="font-medium">{{ (currentPage - 1) * pageSize + 1 }}</span> 到 <span class="font-medium">{{ Math.min(currentPage * pageSize, total) }}</span> 条，共 <span class="font-medium">{{ total }}</span> 条记录
            </p>
          </div>
          <div>
            <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
              <button
                @click="prevPage"
                :disabled="currentPage === 1"
                class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                </svg>
              </button>
              <button
                v-for="page in visiblePages"
                :key="page"
                @click="goToPage(page)"
                class="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium"
                :class="page === currentPage ? 'z-10 text-red-600 bg-red-50 border-red-300' : 'text-gray-500 hover:bg-gray-50'"
              >
                {{ page }}
              </button>
              <button
                @click="nextPage"
                :disabled="currentPage >= totalPages"
                class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </nav>
          </div>
        </div>
      </div>
    </div>

    <!-- 删除确认弹窗 -->
    <div v-if="showDeleteModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl shadow-xl p-6 max-w-md w-full mx-4">
        <div class="text-center">
          <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
            <svg class="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h3 class="mt-4 text-lg font-medium text-gray-900">确认删除</h3>
          <p class="mt-2 text-sm text-gray-500">确定要删除这条心愿便利贴吗？删除后将无法恢复。</p>
        </div>
        <div class="mt-6 flex justify-end space-x-3">
          <button
            @click="showDeleteModal = false"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            取消
          </button>
          <button
            @click="confirmDelete"
            class="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700"
          >
            删除
          </button>
        </div>
      </div>
    </div>

    <!-- 图片预览弹窗 -->
    <div v-if="showImagePreview" class="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50" @click.self="showImagePreview = false">
      <div class="bg-white rounded-xl shadow-xl p-4 max-w-4xl w-full mx-4">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-medium text-gray-900">图片预览</h3>
          <button
            @click="showImagePreview = false"
            class="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <svg class="h-6 w-6 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="flex justify-center items-center bg-gray-100 rounded-lg p-4 min-h-[400px]">
          <img
            :src="previewImageUrl"
            alt="心愿图片"
            class="max-w-full max-h-[500px] object-contain"
          />
        </div>
      </div>
    </div>

    <!-- 发布人信息弹窗 -->
    <div v-if="showPublisherModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl shadow-xl p-6 max-w-md w-full mx-4">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-medium text-gray-900">发布人信息</h3>
          <button
            @click="showPublisherModal = false"
            class="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <svg class="h-6 w-6 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div v-if="publisherInfo" class="space-y-3">
          <div class="flex justify-between py-2 border-b border-gray-100">
            <span class="text-gray-500">用户名</span>
            <span class="font-medium">{{ publisherInfo.user_name }}</span>
          </div>
          <div class="flex justify-between py-2 border-b border-gray-100">
            <span class="text-gray-500">邮箱</span>
            <span class="font-medium">{{ publisherInfo.email || '-' }}</span>
          </div>
          <div class="flex justify-between py-2 border-b border-gray-100">
            <span class="text-gray-500">角色</span>
            <span class="font-medium">{{ publisherInfo.role_name || '-' }}</span>
          </div>
          <div class="flex justify-between py-2 border-b border-gray-100">
            <span class="text-gray-500">班级</span>
            <span class="font-medium">{{ publisherInfo.class_name || '-' }}</span>
          </div>
          <div class="flex justify-between py-2">
            <span class="text-gray-500">注册时间</span>
            <span class="font-medium">{{ formatDate(publisherInfo.created_at) }}</span>
          </div>
        </div>
        <div class="mt-6 flex justify-end">
          <button
            @click="showPublisherModal = false"
            class="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700"
          >
            关闭
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import request from '@/api/request';

const router = useRouter();

const wishList = ref<any[]>([]);
const total = ref(0);
const currentPage = ref(1);
const pageSize = 10;
const searchKeyword = ref('');
const showDeleteModal = ref(false);
const deleteWishId = ref<number | null>(null);
const showImagePreview = ref(false);
const previewImageUrl = ref('');
const showPublisherModal = ref(false);
const publisherInfo = ref<any>(null);

const totalPages = computed(() => Math.ceil(total.value / pageSize));

const visiblePages = computed(() => {
  const pages = [];
  const maxVisible = 5;
  let start = Math.max(1, currentPage.value - Math.floor(maxVisible / 2));
  let end = Math.min(totalPages.value, start + maxVisible - 1);
  start = Math.max(1, end - maxVisible + 1);
  
  for (let i = start; i <= end; i++) {
    pages.push(i);
  }
  return pages;
});

const anonymousCount = computed(() => wishList.value.filter(w => w.is_anonymous).length);
const imageCount = computed(() => wishList.value.filter(w => w.image_url).length);

const loadWishes = async () => {
  currentPage.value = 1;
  await fetchWishes();
};

const fetchWishes = async () => {
  try {
    let url = `/api/v1/wishes/?skip=${(currentPage.value - 1) * pageSize}&limit=${pageSize}`;
    if (searchKeyword.value) {
      url += `&keyword=${encodeURIComponent(searchKeyword.value)}`;
    }
    
    const response = await request.get(url);
    wishList.value = response.items || [];
    total.value = response.total || 0;
  } catch (error) {
    console.error('获取心愿列表失败:', error);
  }
};

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr);
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
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

const goToPage = (page: number) => {
  if (page !== currentPage.value) {
    currentPage.value = page;
    fetchWishes();
  }
};

const deleteWish = (wishId: number) => {
  deleteWishId.value = wishId;
  showDeleteModal.value = true;
};

const confirmDelete = async () => {
  if (!deleteWishId.value) return;
  
  try {
    await request.delete(`/api/v1/wishes/admin/${deleteWishId.value}`);
    showDeleteModal.value = false;
    deleteWishId.value = null;
    await fetchWishes();
  } catch (error) {
    console.error('删除心愿失败:', error);
  }
};

const previewImage = (imageUrl: string) => {
  previewImageUrl.value = imageUrl;
  showImagePreview.value = true;
};

const viewPublisher = async (wish: any) => {
  if (!wish.user_id) return;
  try {
    const data = (await request.get(`/api/v1/admin/users/${wish.user_id}`)) as any;
    publisherInfo.value = {
      user_name: data.real_name || wish.user_name,
      email: data.email,
      role_name: data.role_name,
      class_name: wish.class_name,
      created_at: data.created_at
    };
    showPublisherModal.value = true;
  } catch (error) {
    console.error('获取发布人信息失败:', error);
  }
};

onMounted(() => {
  fetchWishes();
});
</script>