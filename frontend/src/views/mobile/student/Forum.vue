<template>
  <div class="space-y-6">
    <div class="bg-white shadow rounded-lg p-6">
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-2xl font-bold text-gray-900">意见征集</h1>
        <button @click="showCreatePost = true" class="px-4 py-2 bg-primary-600 text-white text-sm rounded-md hover:bg-primary-700">
          发布意见
        </button>
      </div>

      <!-- 帖子列表 -->
      <div class="space-y-4">
        <div v-for="post in posts" :key="post.id" class="border border-gray-200 rounded-lg p-4">
          <div class="flex justify-between items-start">
            <div>
              <h3 class="text-lg font-medium text-gray-900 mb-2">{{ post.title }}</h3>
              <p class="text-sm text-gray-600 mb-3 line-clamp-2">{{ post.content }}</p>
              <div class="flex items-center text-xs text-gray-500 space-x-4">
                <span>{{ post.user_name }} ({{ post.user_role }})</span>
                <span>{{ new Date(post.created_at).toLocaleDateString() }}</span>
                <span class="flex items-center">
                  <svg class="w-3 h-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                  </svg>
                  {{ post.like_count }}
                </span>
                <span class="flex items-center">
                  <svg class="w-3 h-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                  {{ post.comment_count }}
                </span>
              </div>
            </div>
            <button 
              v-if="post.user_id === currentUser?.id"
              @click="deletePost(post.id)"
              class="text-xs text-red-600 hover:text-red-800"
            >
              删除
            </button>
          </div>
          <button 
            @click="viewPostDetail(post)"
            class="mt-3 text-sm text-primary-600 hover:text-primary-800"
          >
            查看详情
          </button>
        </div>
      </div>
    </div>

    <!-- 发布帖子弹窗 -->
    <div v-if="showCreatePost" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold text-gray-900">发布意见</h3>
          <button @click="showCreatePost = false" class="text-gray-500 hover:text-gray-700">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">标题</label>
            <input 
              v-model="newPost.title" 
              type="text" 
              class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
              placeholder="请输入标题"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">内容</label>
            <textarea 
              v-model="newPost.content" 
              class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
              rows="4"
              placeholder="请输入您的意见或建议"
            ></textarea>
          </div>
          <div class="flex justify-end space-x-3">
            <button @click="showCreatePost = false" class="px-4 py-2 border border-gray-300 rounded-md text-sm text-gray-700 hover:bg-gray-50">
              取消
            </button>
            <button @click="createPost" class="px-4 py-2 bg-primary-600 text-white text-sm rounded-md hover:bg-primary-700">
              发布
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 帖子详情弹窗 -->
    <div v-if="showPostDetail" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-md max-h-[80vh] overflow-y-auto">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold text-gray-900">帖子详情</h3>
          <button @click="showPostDetail = false" class="text-gray-500 hover:text-gray-700">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="space-y-4">
          <div>
            <h4 class="text-lg font-medium text-gray-900 mb-2">{{ currentPost.title }}</h4>
            <p class="text-sm text-gray-600 mb-3">{{ currentPost.content }}</p>
            <div class="flex items-center text-xs text-gray-500 space-x-4">
              <span>学员</span>
              <span>{{ new Date(currentPost.created_at).toLocaleDateString() }}</span>
            </div>
            <div class="mt-3 flex items-center space-x-4">
              <button 
                @click="toggleLike" 
                :class="{
                  'flex items-center text-sm': true,
                  'text-primary-600': currentPost.is_liked,
                  'text-gray-600': !currentPost.is_liked
                }"
              >
                <svg 
                  class="w-4 h-4 mr-1" 
                  :class="{ 'fill-primary-600': currentPost.is_liked }"
                  fill="none" 
                  viewBox="0 0 24 24" 
                  stroke="currentColor"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                </svg>
                {{ currentPost.like_count }}
              </button>
            </div>
          </div>
          
          <div class="pt-4 border-t border-gray-200">
            <h5 class="text-sm font-medium text-gray-900 mb-3">评论</h5>
            <div class="space-y-3">
              <div v-for="comment in currentPost.comments" :key="comment.id" class="text-sm">
                <div class="flex justify-between">
                  <span class="text-gray-700">学员</span>
                  <span class="text-gray-500 text-xs">{{ new Date(comment.created_at).toLocaleDateString() }}</span>
                </div>
                <p class="mt-1 text-gray-600">{{ comment.content }}</p>
              </div>
            </div>
            <div class="mt-4">
              <textarea 
                v-model="newComment" 
                class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                rows="2"
                placeholder="写下你的评论..."
              ></textarea>
              <button 
                @click="addComment" 
                class="mt-2 px-4 py-1 bg-primary-600 text-white text-xs rounded-md hover:bg-primary-700"
              >
                评论
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import request from '@/api/request';
import { onMounted, ref } from 'vue';
import { useUserStore } from '@/stores/user';

const userStore = useUserStore();
const currentUser = userStore.user;

const posts = ref<any[]>([]);
const showCreatePost = ref(false);
const showPostDetail = ref(false);
const newPost = ref({ title: '', content: '' });
const currentPost = ref({ id: 0, title: '', content: '', created_at: '', like_count: 0, comment_count: 0, is_owner: false, is_liked: false, comments: [] });
const newComment = ref('');

// 获取帖子列表
const fetchPosts = async () => {
  try {
    const response = await request.get('/api/v1/suggestions/posts');
    if (response && response.items) {
      posts.value = response.items;
    }
  } catch (error) {
    console.error('获取帖子列表失败:', error);
  }
};

// 发布帖子
const createPost = async () => {
  if (!newPost.value.title || !newPost.value.content) {
    alert('请填写标题和内容');
    return;
  }
  try {
    await request.post('/api/v1/suggestions/posts', { ...newPost.value });
    showCreatePost.value = false;
    newPost.value = { title: '', content: '' };
    await fetchPosts();
    alert('发布成功');
  } catch (error) {
    console.error('发布帖子失败:', error);
    alert('发布失败，请稍后重试');
  }
};

// 删除帖子
const deletePost = async (postId: number) => {
  if (confirm('确定要删除这个帖子吗？')) {
    try {
      await request.delete(`/api/v1/suggestions/posts/${postId}`);
      await fetchPosts();
      alert('删除成功');
    } catch (error) {
      console.error('删除帖子失败:', error);
      alert('删除失败，请稍后重试');
    }
  }
};

// 查看帖子详情
const viewPostDetail = async (post: any) => {
  try {
    const response = await request.get(`/api/v1/suggestions/posts/${post.id}`);
    if (response) {
      currentPost.value = response;
      // 获取评论列表
      const commentsResponse = await request.get(`/api/v1/suggestions/posts/${post.id}/comments`);
      if (commentsResponse && commentsResponse.items) {
        currentPost.value.comments = commentsResponse.items;
      }
      showPostDetail.value = true;
    }
  } catch (error) {
    console.error('获取帖子详情失败:', error);
  }
};

// 点赞/取消点赞
const toggleLike = async () => {
  try {
    await request.post(`/api/v1/suggestions/posts/${currentPost.value.id}/like`);
    currentPost.value.is_liked = !currentPost.value.is_liked;
    currentPost.value.like_count += currentPost.value.is_liked ? 1 : -1;
  } catch (error) {
    console.error('点赞失败:', error);
  }
};

// 添加评论
const addComment = async () => {
  if (!newComment.value) {
    alert('请填写评论内容');
    return;
  }
  try {
    await request.post(`/api/v1/suggestions/comments`, { post_id: currentPost.value.id, content: newComment.value });
    newComment.value = '';
    await viewPostDetail(currentPost.value);
  } catch (error) {
    console.error('添加评论失败:', error);
    alert('评论失败，请稍后重试');
  }
};

onMounted(async () => {
  await fetchPosts();
});
</script>