<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-900">意见征集</h1>
      <button @click="showCreateModal = true" class="btn-primary">
        发布征集
      </button>
    </div>

    <!-- 意见征集列表 -->
    <div class="space-y-4">
      <div
        v-for="suggestion in suggestions"
        :key="suggestion.id"
        class="bg-white shadow rounded-lg p-6 hover:shadow-md transition-shadow"
      >
        <div class="flex justify-between items-start">
          <div>
            <h3 class="text-lg font-semibold text-gray-900">{{ suggestion.title }}</h3>
            <p class="text-sm text-gray-500 mt-1">
              {{ suggestion.author_name }} · {{ formatDate(suggestion.created_at) }}
            </p>
          </div>
          <span
            class="px-2 py-1 text-xs font-semibold rounded-full"
            :class="suggestion.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'"
          >
            {{ suggestion.status === 'active' ? '进行中' : '已结束' }}
          </span>
        </div>
        <p class="text-gray-600 mt-3">{{ suggestion.content }}</p>
        <div class="flex justify-between items-center mt-4">
          <div class="flex items-center space-x-4">
            <button
              @click="handleLike(suggestion)"
              class="flex items-center text-gray-500 hover:text-primary-600"
            >
              <svg
                class="h-5 w-5 mr-1"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
                />
              </svg>
              {{ suggestion.like_count }}
            </button>
            <button
              @click="handleComment(suggestion)"
              class="flex items-center text-gray-500 hover:text-primary-600"
            >
              <svg
                class="h-5 w-5 mr-1"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                />
              </svg>
              {{ suggestion.comment_count }}
            </button>
          </div>
          <router-link
            :to="`/assistant/suggestion/${suggestion.id}`"
            class="text-primary-600 hover:text-primary-500 text-sm font-medium"
          >
            查看详情
          </router-link>
        </div>
      </div>
    </div>

    <div v-if="suggestions.length === 0" class="text-center py-12">
      <p class="text-gray-500">暂无意见征集</p>
    </div>

    <!-- 创建意见征集弹窗 -->
    <div
      v-if="showCreateModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 class="text-xl font-bold mb-4">发布意见征集</h2>
        <form @submit.prevent="handleCreateSuggestion">
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                标题
              </label>
              <input
                v-model="createForm.title"
                type="text"
                class="input"
                placeholder="请输入标题"
                required
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                内容
              </label>
              <textarea
                v-model="createForm.content"
                class="input"
                rows="4"
                placeholder="请输入内容"
                required
              ></textarea>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                状态
              </label>
              <select v-model="createForm.status" class="input">
                <option value="active">进行中</option>
                <option value="closed">已结束</option>
              </select>
            </div>
          </div>
          <div class="flex justify-end space-x-3 mt-6">
            <button type="button" @click="showCreateModal = false" class="btn-secondary">
              取消
            </button>
            <button type="submit" class="btn-primary">
              发布
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import request from '@/api/request';

const suggestions = ref<any[]>([]);
const showCreateModal = ref(false);

const createForm = ref({
  title: '',
  content: '',
  status: 'active'
});

// 获取意见征集列表
const fetchSuggestions = async () => {
  try {
    const data = await request.get('/api/v1/suggestions/posts');
    suggestions.value = (data as any).items || [];
  } catch (error) {
    console.error('获取意见征集列表失败:', error);
    suggestions.value = [];
  }
};

// 处理点赞
const handleLike = async (suggestion: any) => {
  try {
    await request.post(`/api/v1/suggestions/posts/${suggestion.id}/like`);
    suggestion.like_count += 1;
  } catch (error) {
    console.error('点赞失败:', error);
  }
};

// 处理评论
const handleComment = (suggestion: any) => {
  // 跳转到详情页进行评论
  window.location.href = `/assistant/suggestion/${suggestion.id}`;
};

// 创建意见征集
const handleCreateSuggestion = async () => {
  try {
    await request.post('/api/v1/suggestions/posts', {
      title: createForm.value.title,
      content: createForm.value.content
    });
    showCreateModal.value = false;
    createForm.value = {
      title: '',
      content: '',
      status: 'active'
    };
    await fetchSuggestions();
    alert('发布成功');
  } catch (error) {
    console.error('发布失败:', error);
    alert('发布失败，请稍后重试');
  }
};

// 格式化日期
const formatDate = (dateString: string) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN');
};

onMounted(async () => {
  await fetchSuggestions();
});
</script>
