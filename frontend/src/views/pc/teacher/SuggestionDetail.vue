<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-900">意见详情</h1>
      <button @click="router.back()" class="btn-secondary">返回</button>
    </div>

    <!-- 帖子内容 -->
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-xl font-semibold mb-4">{{ post?.title }}</h2>
      <div class="flex items-center text-sm text-gray-500 mb-4">
        <span>{{ post?.user_name }} ({{ post?.user_role }})</span>
        <span class="mx-2">|</span>
        <span>{{ formatDate(post?.created_at) }}</span>
        <span class="mx-2">|</span>
        <span>浏览 {{ post?.view_count }}</span>
        <span class="mx-2">|</span>
        <span>点赞 {{ post?.like_count }}</span>
        <span class="mx-2">|</span>
        <span>评论 {{ post?.comment_count }}</span>
      </div>
      <div class="text-gray-700 mb-6">{{ post?.content }}</div>
      <div class="flex space-x-2">
        <button @click="toggleLike" :class="[post?.is_liked ? 'btn-primary' : 'btn-secondary']">
          {{ post?.is_liked ? '已点赞' : '点赞' }}
        </button>
        <button v-if="post?.user_id === userStore.user?.id" @click="editPost" class="btn-secondary">编辑</button>
        <button v-if="post?.user_id === userStore.user?.id || userStore.user?.role?.role_name === 'admin' || userStore.user?.role?.role_name === 'super_admin'" @click="deletePost" class="btn-danger">删除</button>
      </div>
    </div>

    <!-- 评论区 -->
    <div class="bg-white rounded-lg shadow p-6">
      <h3 class="text-lg font-semibold mb-4">评论 ({{ comments.length }})</h3>
      
      <!-- 评论输入框 -->
      <div class="mb-6">
        <textarea v-model="commentContent" class="input w-full" rows="3" placeholder="请输入评论"></textarea>
        <div class="flex justify-end mt-2">
          <button @click="submitComment" class="btn-primary" :disabled="!commentContent">提交评论</button>
        </div>
      </div>

      <!-- 评论列表 -->
      <div class="space-y-4">
        <div v-for="comment in comments" :key="comment.id" class="border-b border-gray-200 pb-4">
          <div class="flex justify-between items-start">
            <div>
              <div class="flex items-center text-sm text-gray-500 mb-2">
                <span>{{ comment.user_name }} ({{ comment.user_role }})</span>
                <span class="mx-2">|</span>
                <span>{{ formatDate(comment.created_at) }}</span>
              </div>
              <p class="text-gray-700">{{ comment.content }}</p>
            </div>
            <div class="flex space-x-2">
              <button v-if="comment.user_id === userStore.user?.id" @click="editComment(comment)" class="btn-secondary text-xs">编辑</button>
              <button v-if="comment.user_id === userStore.user?.id || userStore.user?.role?.role_name === 'admin' || userStore.user?.role?.role_name === 'super_admin'" @click="deleteComment(comment.id)" class="btn-danger text-xs">删除</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 分页 -->
      <div class="flex justify-center mt-6">
        <div class="flex space-x-2">
          <button @click="handleCommentPageChange(1)" :disabled="commentCurrentPage === 1" class="btn-secondary">首页</button>
          <button @click="handleCommentPageChange(commentCurrentPage - 1)" :disabled="commentCurrentPage === 1" class="btn-secondary">上一页</button>
          <button class="btn-primary">{{ commentCurrentPage }}</button>
          <button @click="handleCommentPageChange(commentCurrentPage + 1)" :disabled="commentCurrentPage >= commentTotalPages" class="btn-secondary">下一页</button>
          <button @click="handleCommentPageChange(commentTotalPages)" :disabled="commentCurrentPage >= commentTotalPages" class="btn-secondary">末页</button>
        </div>
      </div>
    </div>

    <!-- 编辑帖子弹窗 -->
    <div v-if="showEditModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-2xl">
        <h3 class="text-lg font-bold mb-4">编辑意见</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">标题</label>
            <input v-model="editForm.title" type="text" class="input w-full" placeholder="请输入标题" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">内容</label>
            <textarea v-model="editForm.content" class="input w-full" rows="6" placeholder="请输入内容"></textarea>
          </div>
          <div class="flex justify-end space-x-3">
            <button @click="showEditModal = false; resetEditForm()" class="btn-secondary">取消</button>
            <button @click="updatePost" class="btn-primary" :disabled="!editForm.title || !editForm.content">保存</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 编辑评论弹窗 -->
    <div v-if="showEditCommentModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-2xl">
        <h3 class="text-lg font-bold mb-4">编辑评论</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">内容</label>
            <textarea v-model="editCommentForm.content" class="input w-full" rows="4" placeholder="请输入评论"></textarea>
          </div>
          <div class="flex justify-end space-x-3">
            <button @click="showEditCommentModal = false; resetEditCommentForm()" class="btn-secondary">取消</button>
            <button @click="updateComment" class="btn-primary" :disabled="!editCommentForm.content">保存</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useUserStore } from '@/stores/user';
import request from '@/api/request';

const router = useRouter();
const route = useRoute();
const userStore = useUserStore();

// 状态
const post = ref<any>(null);
const comments = ref<any[]>([]);
const commentTotal = ref(0);
const commentCurrentPage = ref(1);
const pageSize = 20;
const commentContent = ref('');

// 弹窗状态
const showEditModal = ref(false);
const showEditCommentModal = ref(false);
const editForm = ref({ id: 0, title: '', content: '' });
const editCommentForm = ref({ id: 0, content: '' });

// 计算属性
const commentTotalPages = computed(() => Math.ceil(commentTotal.value / pageSize));

// 方法
const fetchPost = async () => {
  try {
    const postId = route.params.id;
    const response = await request.get(`/api/v1/suggestions/posts/${postId}`);
    post.value = response;
  } catch (error) {
    console.error('获取帖子详情失败:', error);
  }
};

const fetchComments = async () => {
  try {
    const postId = route.params.id;
    const response = await request.get(`/api/v1/suggestions/posts/${postId}/comments`, {
      params: {
        skip: (commentCurrentPage.value - 1) * pageSize,
        limit: pageSize
      }
    });
    if (response && response.items) {
      comments.value = response.items;
      commentTotal.value = response.total || 0;
    }
  } catch (error) {
    console.error('获取评论列表失败:', error);
  }
};

const submitComment = async () => {
  try {
    const postId = route.params.id;
    await request.post('/api/v1/suggestions/comments', {
      post_id: postId,
      content: commentContent.value
    });
    commentContent.value = '';
    fetchComments();
    fetchPost();
  } catch (error) {
    console.error('提交评论失败:', error);
  }
};

const toggleLike = async () => {
  try {
    const postId = route.params.id;
    const response = await request.post(`/api/v1/suggestions/posts/${postId}/like`);
    if (response.success) {
      post.value.like_count = response.like_count;
      post.value.is_liked = response.is_liked;
    }
  } catch (error) {
    console.error('点赞/取消点赞失败:', error);
  }
};

const editPost = () => {
  editForm.value = { id: post.value.id, title: post.value.title, content: post.value.content };
  showEditModal.value = true;
};

const updatePost = async () => {
  try {
    await request.put(`/api/v1/suggestions/posts/${editForm.value.id}`, editForm.value);
    showEditModal.value = false;
    resetEditForm();
    fetchPost();
  } catch (error) {
    console.error('更新帖子失败:', error);
  }
};

const deletePost = async () => {
  if (confirm('确定要删除这篇帖子吗？')) {
    try {
      const postId = route.params.id;
      await request.delete(`/api/v1/suggestions/posts/${postId}`);
      router.push('/teacher/suggestion-forum');
    } catch (error) {
      console.error('删除帖子失败:', error);
    }
  }
};

const editComment = (comment: any) => {
  editCommentForm.value = { id: comment.id, content: comment.content };
  showEditCommentModal.value = true;
};

const updateComment = async () => {
  try {
    await request.put(`/api/v1/suggestions/comments/${editCommentForm.value.id}`, editCommentForm.value);
    showEditCommentModal.value = false;
    resetEditCommentForm();
    fetchComments();
  } catch (error) {
    console.error('更新评论失败:', error);
  }
};

const deleteComment = async (commentId: number) => {
  if (confirm('确定要删除这条评论吗？')) {
    try {
      await request.delete(`/api/v1/suggestions/comments/${commentId}`);
      fetchComments();
      fetchPost();
    } catch (error) {
      console.error('删除评论失败:', error);
    }
  }
};

const handleCommentPageChange = (page: number) => {
  if (page >= 1 && page <= commentTotalPages.value) {
    commentCurrentPage.value = page;
    fetchComments();
  }
};

const resetEditForm = () => {
  editForm.value = { id: 0, title: '', content: '' };
};

const resetEditCommentForm = () => {
  editCommentForm.value = { id: 0, content: '' };
};

const formatDate = (date: string) => {
  return new Date(date).toLocaleString();
};

// 生命周期
onMounted(() => {
  fetchPost();
  fetchComments();
});
</script>
