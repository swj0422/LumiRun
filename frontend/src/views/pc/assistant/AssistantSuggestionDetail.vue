<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-900">意见征集详情</h1>
      <router-link to="/assistant/suggestion-forum" class="btn-secondary">
        返回列表
      </router-link>
    </div>

    <!-- 意见征集详情 -->
    <div class="bg-white shadow rounded-lg p-6">
      <div class="flex justify-between items-start">
        <div>
          <h2 class="text-xl font-bold text-gray-900">{{ suggestion.title }}</h2>
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
      <div class="mt-4 text-gray-700">
        {{ suggestion.content }}
      </div>
      <div class="flex justify-between items-center mt-6">
        <button
          @click="handleLike"
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
        <span class="text-gray-500">
          {{ suggestion.comment_count }} 条评论
        </span>
      </div>
    </div>

    <!-- 评论列表 -->
    <div class="bg-white shadow rounded-lg p-6">
      <h3 class="text-lg font-semibold text-gray-900 mb-4">评论</h3>
      <div class="space-y-4">
        <div v-for="comment in comments" :key="comment.id" class="border-b pb-4">
          <div class="flex justify-between items-start">
            <div>
              <p class="text-sm font-medium text-gray-900">{{ comment.user_name }}</p>
              <p class="text-sm text-gray-500 mt-1">{{ formatDate(comment.created_at) }}</p>
            </div>
          </div>
          <p class="text-gray-700 mt-2">{{ comment.content }}</p>
        </div>
      </div>
      <div v-if="comments.length === 0" class="text-center py-8">
        <p class="text-gray-500">暂无评论</p>
      </div>

      <!-- 发表评论 -->
      <div class="mt-6">
        <h4 class="text-sm font-medium text-gray-700 mb-2">发表评论</h4>
        <form @submit.prevent="handleComment">
          <textarea
            v-model="commentForm.content"
            class="input mb-4"
            rows="3"
            placeholder="请输入评论内容"
            required
          ></textarea>
          <button type="submit" class="btn-primary">
            发表评论
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import request from '@/api/request';

const route = useRoute();
const suggestion = ref({
  id: '',
  title: '',
  content: '',
  author_name: '',
  created_at: '',
  status: '',
  like_count: 0,
  comment_count: 0
});
const comments = ref<any[]>([]);

const commentForm = ref({
  content: ''
});

// 获取意见征集详情
const fetchSuggestionDetail = async () => {
  const id = route.params.id;
  if (!id) return;

  try {
    const data = await request.get(`/api/v1/suggestions/posts/${id}`);
    suggestion.value = {
      ...data,
      author_name: data.user_name,
      status: 'active' // 默认为进行中，因为后端API没有返回状态字段
    };
  } catch (error) {
    console.error('获取意见征集详情失败:', error);
  }
};

// 获取评论列表
const fetchComments = async () => {
  const id = route.params.id;
  if (!id) return;

  try {
    const data = await request.get(`/api/v1/suggestions/posts/${id}/comments`);
    comments.value = (data as any).items || [];
  } catch (error) {
    console.error('获取评论列表失败:', error);
    comments.value = [];
  }
};

// 处理点赞
const handleLike = async () => {
  const id = route.params.id;
  if (!id) return;

  try {
    await request.post(`/api/v1/suggestions/posts/${id}/like`);
    suggestion.value.like_count += 1;
  } catch (error) {
    console.error('点赞失败:', error);
  }
};

// 发表评论
const handleComment = async () => {
  const id = route.params.id;
  if (!id || !commentForm.value.content) return;

  try {
    await request.post(`/api/v1/suggestions/comments`, {
      post_id: id,
      content: commentForm.value.content
    });
    commentForm.value.content = '';
    await fetchComments();
    suggestion.value.comment_count += 1;
    alert('评论成功');
  } catch (error) {
    console.error('发表评论失败:', error);
    alert('发表评论失败，请稍后重试');
  }
};

// 格式化日期
const formatDate = (dateString: string) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN');
};

onMounted(async () => {
  await fetchSuggestionDetail();
  await fetchComments();
});
</script>
