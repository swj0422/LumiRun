<template>
  <div class="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-orange-50">
    <!-- 顶部导航 -->
    <div class="bg-white/80 backdrop-blur-sm shadow-sm sticky top-0 z-40">
      <div class="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
        <h1 class="text-2xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
          ✨ 心愿便利贴
        </h1>
        <button
          @click="showCreateModal = true"
          class="px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105 flex items-center space-x-2"
        >
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          <span>发布心愿</span>
        </button>
      </div>
    </div>

    <!-- 主内容区 - 瀑布流 -->
    <div class="max-w-6xl mx-auto px-4 py-8">
      <!-- 温馨提示 -->
      <div class="text-center mb-8">
        <p class="text-gray-500 text-sm">
          💌 在这里写下你的心愿，与大家分享美好期许
        </p>
      </div>

      <!-- 瀑布流容器 -->
      <div class="columns-1 md:columns-2 lg:columns-3 gap-6 space-y-6">
        <div
          v-for="wish in wishList"
          :key="wish.id"
          class="break-inside-avoid mb-6"
        >
          <div
            class="bg-white rounded-2xl shadow-md hover:shadow-lg transition-all duration-300 overflow-hidden transform hover:-translate-y-1"
            :class="getRandomBgClass()"
          >
            <!-- 卡片内容 -->
            <div class="p-6 relative">
              <!-- 删除按钮（仅自己的心愿或管理员可见） -->
              <button
                v-if="canDelete(wish)"
                @click="deleteWish(wish.id)"
                class="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-gray-100 rounded-full"
              >
                <svg class="w-4 h-4 text-gray-400 hover:text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>

              <!-- 心愿内容 -->
              <p class="text-gray-700 leading-relaxed mb-4 whitespace-pre-wrap">{{ wish.content }}</p>

              <!-- 图片 -->
              <div v-if="wish.image_url" class="rounded-xl overflow-hidden mb-4">
                <img
                  :src="wish.image_url"
                  class="w-full h-48 object-cover"
                  alt="心愿图片"
                />
              </div>

              <!-- 底部：用户信息和时间（右下角） -->
              <div class="flex items-center justify-end space-x-2 mt-4 pt-3 border-t border-gray-100">
                <div>
                  <p class="text-xs text-gray-400">{{ formatDate(wish.created_at) }}</p>
                  <p class="text-sm font-medium text-gray-800">
                    {{ wish.is_anonymous ? '匿名用户' : wish.user_name }}
                  </p>
                </div>
                <div class="w-7 h-7 rounded-full flex items-center justify-center" :class="getRandomAvatarBg()">
                  <svg v-if="wish.is_anonymous" class="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                  <span v-else class="text-white font-medium text-xs">{{ wish.user_name?.charAt(0) || '?' }}</span>
                </div>
              </div>
            </div>

            <!-- 底部装饰 -->
            <div class="h-1" :class="getRandomBorderClass()"></div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="wishList.length === 0" class="text-center py-16">
        <div class="w-24 h-24 bg-gradient-to-br from-purple-100 to-pink-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <svg class="w-12 h-12 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
          </svg>
        </div>
        <h3 class="text-xl font-medium text-gray-600 mb-2">还没有心愿</h3>
        <p class="text-gray-400 mb-6">成为第一个分享心愿的人吧 ✨</p>
        <button
          @click="showCreateModal = true"
          class="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-full shadow-lg hover:shadow-xl transition-all"
        >
          发布第一个心愿
        </button>
      </div>

      <!-- 加载更多 -->
      <div v-if="total > wishList.length" class="text-center py-8">
        <button
          @click="loadMore"
          class="px-6 py-3 border-2 border-purple-300 text-purple-600 rounded-full hover:bg-purple-50 transition-all"
        >
          加载更多心愿
        </button>
      </div>
    </div>

    <!-- 发布心愿弹窗 -->
    <div
      v-if="showCreateModal"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
    >
      <div class="bg-white rounded-2xl w-full max-w-lg overflow-hidden shadow-2xl">
        <!-- 弹窗头部 -->
        <div class="bg-gradient-to-r from-purple-500 to-pink-500 px-6 py-4">
          <div class="flex justify-between items-center">
            <h3 class="text-lg font-semibold text-white">发布心愿</h3>
            <button
              @click="closeModal"
              class="text-white/80 hover:text-white"
            >
              <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <!-- 弹窗内容 -->
        <div class="p-6">
          <!-- 文字内容 -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">心愿内容</label>
            <textarea
              v-model="formData.content"
              placeholder="写下你的心愿（1-200字）..."
              rows="4"
              class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
              :class="{ 'border-red-300': contentError }"
            ></textarea>
            <p class="text-xs text-gray-400 mt-1 text-right">{{ formData.content.length }}/200</p>
            <p v-if="contentError" class="text-xs text-red-500 mt-1">{{ contentError }}</p>
          </div>

          <!-- 图片上传 -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">添加图片（可选）</label>
            <div class="flex space-x-3">
              <div
                v-if="formData.image"
                class="relative w-20 h-20 rounded-xl overflow-hidden"
              >
                <img :src="formData.image" class="w-full h-full object-cover" />
                <button
                  @click="removeImage"
                  class="absolute top-1 right-1 w-6 h-6 bg-black/50 rounded-full flex items-center justify-center"
                >
                  <svg class="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <div
                v-else
                @click="triggerFileInput"
                class="w-20 h-20 rounded-xl border-2 border-dashed border-gray-300 flex items-center justify-center cursor-pointer hover:border-purple-400 transition-colors"
              >
                <svg class="w-8 h-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
            </div>
            <p class="text-xs text-gray-400 mt-2">支持 JPG、PNG 格式，最多1张</p>
          </div>

          <!-- 匿名开关 -->
          <div class="mb-6">
            <label class="flex items-center justify-between cursor-pointer">
              <span class="text-sm font-medium text-gray-700">匿名发布</span>
              <div
                @click="formData.isAnonymous = !formData.isAnonymous"
                class="relative w-12 h-6 rounded-full transition-colors"
                :class="formData.isAnonymous ? 'bg-purple-500' : 'bg-gray-300'"
              >
                <div
                  class="absolute top-1 w-4 h-4 bg-white rounded-full transition-transform shadow"
                  :class="formData.isAnonymous ? 'translate-x-7' : 'translate-x-1'"
                ></div>
              </div>
            </label>
            <p class="text-xs text-gray-400 mt-1">开启后将隐藏你的身份信息</p>
          </div>

          <!-- 提交按钮 -->
          <button
            @click="submitWish"
            :disabled="!formData.content.trim() || isSubmitting"
            class="w-full py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-xl font-medium shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ isSubmitting ? '发布中...' : '发布心愿' }}
          </button>
        </div>
      </div>

      <!-- 文件输入 -->
      <input
        ref="fileInput"
        type="file"
        accept="image/*"
        class="hidden"
        @change="handleFileSelect"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import request from '@/api/request';
import { useUserStore } from '@/stores/user';

const userStore = useUserStore();
const wishList = ref<any[]>([]);
const total = ref(0);
const skip = ref(0);
const limit = 20;

const showCreateModal = ref(false);
const isSubmitting = ref(false);
const contentError = ref('');
const fileInput = ref<HTMLInputElement | null>(null);

const formData = ref({
  content: '',
  image: '',
  isAnonymous: false
});

// 随机背景色类
const bgClasses = [
  'bg-gradient-to-br from-purple-50 to-pink-50',
  'bg-gradient-to-br from-pink-50 to-orange-50',
  'bg-gradient-to-br from-blue-50 to-purple-50',
  'bg-gradient-to-br from-green-50 to-blue-50',
  'bg-gradient-to-br from-yellow-50 to-orange-50',
  'bg-gradient-to-br from-pink-50 to-red-50'
];

const borderClasses = [
  'bg-gradient-to-r from-purple-400 to-pink-400',
  'bg-gradient-to-r from-pink-400 to-orange-400',
  'bg-gradient-to-r from-blue-400 to-purple-400',
  'bg-gradient-to-r from-green-400 to-blue-400',
  'bg-gradient-to-r from-yellow-400 to-orange-400'
];

const avatarBgClasses = [
  'bg-gradient-to-br from-purple-500 to-pink-500',
  'bg-gradient-to-br from-pink-500 to-orange-500',
  'bg-gradient-to-br from-blue-500 to-purple-500',
  'bg-gradient-to-br from-green-500 to-blue-500',
  'bg-gradient-to-br from-yellow-500 to-orange-500'
];

const getRandomBgClass = () => bgClasses[Math.floor(Math.random() * bgClasses.length)];
const getRandomBorderClass = () => borderClasses[Math.floor(Math.random() * borderClasses.length)];
const getRandomAvatarBg = () => avatarBgClasses[Math.floor(Math.random() * avatarBgClasses.length)];

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr);
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  
  const hours = date.getHours().toString().padStart(2, '0');
  const minutes = date.getMinutes().toString().padStart(2, '0');
  const timeStr = `${hours}:${minutes}`;
  
  if (days === 0) return `今天 ${timeStr}`;
  if (days === 1) return `昨天 ${timeStr}`;
  if (days < 7) return `${days}天前 ${timeStr}`;
  return `${date.toLocaleDateString('zh-CN')} ${timeStr}`;
};

const fetchWishes = async (loadMore = false) => {
  try {
    const currentSkip = loadMore ? skip.value : 0;
    const response = await request.get(`/api/v1/wishes/?skip=${currentSkip}&limit=${limit}`);
    if (response && response.items) {
      if (loadMore) {
        wishList.value = [...wishList.value, ...response.items];
      } else {
        wishList.value = response.items;
      }
      total.value = response.total;
      skip.value = currentSkip + limit;
    }
  } catch (error) {
    console.error('获取心愿列表失败:', error);
  }
};

const closeModal = () => {
  showCreateModal.value = false;
  formData.value = { content: '', image: '', isAnonymous: false };
  contentError.value = '';
};

const triggerFileInput = () => {
  fileInput.value?.click();
};

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement;
  const files = target.files;
  if (files && files[0]) {
    const reader = new FileReader();
    reader.onload = (e) => {
      formData.value.image = e.target?.result as string;
    };
    reader.readAsDataURL(files[0]);
  }
};

const removeImage = () => {
  formData.value.image = '';
};

const submitWish = async () => {
  // 验证
  if (!formData.value.content.trim()) {
    contentError.value = '请输入心愿内容';
    return;
  }
  if (formData.value.content.length > 200) {
    contentError.value = '心愿内容不能超过200字';
    return;
  }
  contentError.value = '';

  isSubmitting.value = true;

  try {
    const form = new FormData();
    form.append('content', formData.value.content);
    form.append('is_anonymous', String(formData.value.isAnonymous));

    if (formData.value.image && formData.value.image.startsWith('data:')) {
      const blob = await fetch(formData.value.image).then(res => res.blob());
      form.append('image', blob, `wish_${Date.now()}.jpg`);
    }

    await request.post('/api/v1/wishes/', form, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });

    closeModal();
    await fetchWishes();
  } catch (error) {
    console.error('发布心愿失败:', error);
    alert('发布失败，请稍后重试');
  } finally {
    isSubmitting.value = false;
  }
};

const canDelete = (wish: any) => {
  // 自己的心愿或管理员
  return wish.user_id === userStore.userInfo?.id || 
         userStore.userInfo?.role_name === 'super_admin' || 
         userStore.userInfo?.role_name === 'admin';
};

const deleteWish = async (wishId: number) => {
  if (!confirm('确定要删除这个心愿吗？删除后不可恢复。')) {
    return;
  }

  try {
    await request.delete(`/api/v1/wishes/${wishId}`);
    wishList.value = wishList.value.filter(w => w.id !== wishId);
    total.value--;
  } catch (error) {
    console.error('删除心愿失败:', error);
    alert('删除失败，请稍后重试');
  }
};

const loadMore = () => {
  fetchWishes(true);
};

onMounted(() => {
  fetchWishes();
});
</script>