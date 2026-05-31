<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-900">意见征集管理</h1>
    </div>

    <div class="bg-white rounded-lg shadow p-4">
      <div class="flex flex-wrap gap-4">
        <select v-model="selectedClass" class="input w-48" @change="fetchPosts">
          <option value="">全部组织</option>
          <option v-for="cls in classes" :key="cls.id" :value="cls.id">{{ cls.class_name }}</option>
        </select>
      </div>
    </div>

    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">标题</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">内容</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">发布人</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">组织</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">评论数</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">发布时间</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="post in posts" :key="post.id">
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ post.title }}</td>
            <td class="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">{{ post.content }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ post.author_name }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ post.class_name }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ post.comment_count }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ formatDate(post.created_at) }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
              <button @click="viewComments(post)" class="text-blue-600 hover:text-blue-700 mr-2">评论</button>
              <button @click="deletePost(post)" class="text-red-600 hover:text-red-700">删除</button>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="posts.length === 0" class="text-center py-12">
        <p class="text-gray-500">暂无意见征集数据</p>
      </div>
    </div>

    <div v-if="showCommentsModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl p-6 w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-bold">评论管理 - {{ selectedPost?.title }}</h2>
          <button @click="showCommentsModal = false" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="flex-1 overflow-y-auto">
          <div v-if="comments.length === 0" class="text-center py-8">
            <p class="text-gray-500">暂无评论</p>
          </div>
          <div v-else class="space-y-4">
            <div v-for="comment in comments" :key="comment.id" class="border-b border-gray-100 pb-4">
              <div class="flex justify-between items-start">
                <div class="flex-1">
                  <p class="text-sm font-medium text-gray-900">{{ comment.author_name }}</p>
                  <p class="text-sm text-gray-600 mt-1">{{ comment.content }}</p>
                  <p class="text-xs text-gray-400 mt-2">{{ formatDate(comment.created_at) }}</p>
                </div>
                <button @click="deleteComment(comment.id)" class="text-red-600 hover:text-red-700 text-sm">删除</button>
              </div>
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

interface Post {
  id: number;
  title: string;
  content: string;
  author_name: string;
  class_name: string;
  comment_count: number;
  created_at: string;
}

interface Comment {
  id: number;
  content: string;
  author_name: string;
  created_at: string;
}

interface ClassInfo {
  id: number;
  class_name: string;
}

const posts = ref<Post[]>([]);
const classes = ref<ClassInfo[]>([]);
const comments = ref<Comment[]>([]);
const selectedClass = ref('');
const showCommentsModal = ref(false);
const selectedPost = ref<Post | null>(null);

const fetchPosts = async () => {
  try {
    const params: Record<string, any> = {};
    if (selectedClass.value) params.class_id = selectedClass.value;
    const data = (await request.get('/api/v1/admin/suggestions', { params })) as { items: Post[] };
    posts.value = data.items || [];
  } catch (error) {
    console.error('获取意见征集列表失败:', error);
  }
};

const fetchClasses = async () => {
  try {
    const data = (await request.get('/api/v1/admin/classes')) as { items: ClassInfo[] };
    classes.value = data.items || [];
  } catch (error) {
    console.error('获取组织列表失败:', error);
  }
};

const viewComments = async (post: Post) => {
  selectedPost.value = post;
  try {
    const data = (await request.get(`/api/v1/admin/suggestions/${post.id}/comments`)) as { items: Comment[] };
    comments.value = data.items || [];
    showCommentsModal.value = true;
  } catch (error) {
    console.error('获取评论列表失败:', error);
  }
};

const deletePost = async (post: Post) => {
  if (!confirm(`确定要删除帖子"${post.title}"吗？删除后所有评论也将被删除。`)) return;
  try {
    await request.delete(`/api/v1/admin/suggestions/${post.id}`);
    fetchPosts();
  } catch (error) {
    console.error('删除帖子失败:', error);
  }
};

const deleteComment = async (commentId: number) => {
  if (!confirm('确定要删除该评论吗？')) return;
  try {
    await request.delete(`/api/v1/admin/suggestions/comments/${commentId}`);
    if (selectedPost.value) {
      const data = (await request.get(`/api/v1/admin/suggestions/${selectedPost.value.id}/comments`)) as { items: Comment[] };
      comments.value = data.items || [];
    }
    fetchPosts();
  } catch (error) {
    console.error('删除评论失败:', error);
  }
};

const formatDate = (date: string) => {
  return new Date(date).toLocaleString('zh-CN');
};

onMounted(() => {
  fetchPosts();
  fetchClasses();
});
</script>
