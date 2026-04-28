<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-900">意见征集</h1>
      <button @click="openCreateModal" class="btn-primary">发布意见</button>
    </div>

    <!-- 排序和筛选 -->
    <div class="bg-white rounded-lg shadow p-4">
      <div class="flex items-center gap-4">
        <select v-model="orderBy" class="input w-48" @change="fetchPosts">
          <option value="created_at">最新发布</option>
          <option value="like_count">最多点赞</option>
          <option value="comment_count">最多评论</option>
        </select>
        <button @click="activeTab = 'myPosts'" :class="[activeTab === 'myPosts' ? 'btn-primary' : 'btn-secondary']">
          我的发布
        </button>
        <button @click="activeTab = 'allPosts'" :class="[activeTab === 'allPosts' ? 'btn-primary' : 'btn-secondary']">
          全部帖子
        </button>
      </div>
    </div>

    <!-- 帖子列表 -->
    <div v-if="activeTab === 'allPosts'" class="space-y-4">
      <div v-for="post in posts" :key="post.id" class="bg-white rounded-lg shadow p-6">
        <div class="flex justify-between items-start">
          <div>
            <h3 class="text-lg font-semibold mb-2">{{ post.title }}</h3>
            <p class="text-gray-600 mb-4">{{ truncateContent(post.content, 100) }}</p>
            <div class="flex items-center text-sm text-gray-500 space-x-4">
              <span>{{ post.user_name }} ({{ post.user_role }})</span>
              <span>{{ formatDate(post.created_at) }}</span>
              <span>浏览 {{ post.view_count }}</span>
              <span>点赞 {{ post.like_count }}</span>
              <span>评论 {{ post.comment_count }}</span>
            </div>
          </div>
          <div class="flex space-x-2">
            <button @click="viewPost(post.id)" class="btn-secondary">查看</button>
            <button v-if="post.user_id === userStore.user?.id" @click="editPost(post)" class="btn-secondary">编辑</button>
            <button v-if="post.user_id === userStore.user?.id || userStore.user?.role?.role_name === 'admin' || userStore.user?.role?.role_name === 'super_admin'" @click="deletePost(post.id)" class="btn-danger">删除</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 我的发布 -->
    <div v-if="activeTab === 'myPosts'" class="space-y-4">
      <div v-for="post in myPosts" :key="post.id" class="bg-white rounded-lg shadow p-6">
        <div class="flex justify-between items-start">
          <div>
            <h3 class="text-lg font-semibold mb-2">{{ post.title }}</h3>
            <p class="text-gray-600 mb-4">{{ truncateContent(post.content, 100) }}</p>
            <div class="flex items-center text-sm text-gray-500 space-x-4">
              <span>{{ post.user_name }} ({{ post.user_role }})</span>
              <span>{{ formatDate(post.created_at) }}</span>
              <span>浏览 {{ post.view_count }}</span>
              <span>点赞 {{ post.like_count }}</span>
              <span>评论 {{ post.comment_count }}</span>
            </div>
          </div>
          <div class="flex space-x-2">
            <button @click="viewPost(post.id)" class="btn-secondary">查看</button>
            <button @click="editPost(post)" class="btn-secondary">编辑</button>
            <button @click="deletePost(post.id)" class="btn-danger">删除</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div v-if="activeTab === 'allPosts'" class="flex justify-center">
      <div class="flex space-x-2">
        <button @click="handlePageChange(1)" :disabled="currentPage === 1" class="btn-secondary">首页</button>
        <button @click="handlePageChange(currentPage - 1)" :disabled="currentPage === 1" class="btn-secondary">上一页</button>
        <button class="btn-primary">{{ currentPage }}</button>
        <button @click="handlePageChange(currentPage + 1)" :disabled="currentPage >= totalPages" class="btn-secondary">下一页</button>
        <button @click="handlePageChange(totalPages)" :disabled="currentPage >= totalPages" class="btn-secondary">末页</button>
      </div>
    </div>

    <!-- 分页 (我的发布) -->
    <div v-if="activeTab === 'myPosts'" class="flex justify-center">
      <div class="flex space-x-2">
        <button @click="handleMyPostsPageChange(1)" :disabled="myPostsCurrentPage === 1" class="btn-secondary">首页</button>
        <button @click="handleMyPostsPageChange(myPostsCurrentPage - 1)" :disabled="myPostsCurrentPage === 1" class="btn-secondary">上一页</button>
        <button class="btn-primary">{{ myPostsCurrentPage }}</button>
        <button @click="handleMyPostsPageChange(myPostsCurrentPage + 1)" :disabled="myPostsCurrentPage >= myPostsTotalPages" class="btn-secondary">下一页</button>
        <button @click="handleMyPostsPageChange(myPostsTotalPages)" :disabled="myPostsCurrentPage >= myPostsTotalPages" class="btn-secondary">末页</button>
      </div>
    </div>

    <!-- 创建帖子弹窗 -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-2xl">
        <h3 class="text-lg font-bold mb-4">发布意见</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">标题</label>
            <input v-model="createForm.title" type="text" class="input w-full" placeholder="请输入标题" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">内容</label>
            <textarea v-model="createForm.content" class="input w-full" rows="6" placeholder="请输入内容"></textarea>
          </div>
          <div class="flex justify-end space-x-3">
            <button @click="showCreateModal = false; resetCreateForm()" class="btn-secondary">取消</button>
            <button @click="createPost" class="btn-primary" :disabled="!createForm.title || !createForm.content">发布</button>
          </div>
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user';
import request from '@/api/request';

const router = useRouter();
const userStore = useUserStore();

// 状态
const posts = ref<any[]>([]);
const myPosts = ref<any[]>([]);
const total = ref(0);
const myPostsTotal = ref(0);
const currentPage = ref(1);
const myPostsCurrentPage = ref(1);
const pageSize = 20;
const orderBy = ref('created_at');
const activeTab = ref('allPosts');

// 弹窗状态
const showCreateModal = ref(false);
const showEditModal = ref(false);
const createForm = ref({ title: '', content: '' });
const editForm = ref({ id: 0, title: '', content: '' });

// 计算属性
const totalPages = computed(() => Math.ceil(total.value / pageSize));
const myPostsTotalPages = computed(() => Math.ceil(myPostsTotal.value / pageSize));

// 方法
const fetchPosts = async () => {
  try {
    const response = await request.get('/api/v1/suggestions/posts', {
      params: {
        skip: (currentPage.value - 1) * pageSize,
        limit: pageSize,
        order_by: orderBy.value
      }
    });
    if (response && response.items) {
      posts.value = response.items;
      total.value = response.total || 0;
    }
  } catch (error) {
    console.error('获取帖子列表失败:', error);
  }
};

const fetchMyPosts = async () => {
  try {
    const response = await request.get('/api/v1/suggestions/user/posts', {
      params: {
        skip: (myPostsCurrentPage.value - 1) * pageSize,
        limit: pageSize
      }
    });
    if (response && response.items) {
      myPosts.value = response.items;
      myPostsTotal.value = response.total || 0;
    }
  } catch (error) {
    console.error('获取我的帖子列表失败:', error);
  }
};

const createPost = async () => {
  try {
    await request.post('/api/v1/suggestions/posts', createForm.value);
    showCreateModal.value = false;
    resetCreateForm();
    fetchPosts();
  } catch (error) {
    console.error('创建帖子失败:', error);
  }
};

const updatePost = async () => {
  try {
    await request.put(`/api/v1/suggestions/posts/${editForm.value.id}`, editForm.value);
    showEditModal.value = false;
    resetEditForm();
    fetchPosts();
    fetchMyPosts();
  } catch (error) {
    console.error('更新帖子失败:', error);
  }
};

const deletePost = async (postId: number) => {
  if (confirm('确定要删除这篇帖子吗？')) {
    try {
      await request.delete(`/api/v1/suggestions/posts/${postId}`);
      fetchPosts();
      fetchMyPosts();
    } catch (error) {
      console.error('删除帖子失败:', error);
    }
  }
};

const viewPost = (postId: number) => {
  router.push(`/teacher/suggestion/${postId}`);
};

const editPost = (post: any) => {
  editForm.value = { id: post.id, title: post.title, content: post.content };
  showEditModal.value = true;
};

const openCreateModal = () => {
  showCreateModal.value = true;
};

const resetCreateForm = () => {
  createForm.value = { title: '', content: '' };
};

const resetEditForm = () => {
  editForm.value = { id: 0, title: '', content: '' };
};

const handlePageChange = (page: number) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page;
    fetchPosts();
  }
};

const handleMyPostsPageChange = (page: number) => {
  if (page >= 1 && page <= myPostsTotalPages.value) {
    myPostsCurrentPage.value = page;
    fetchMyPosts();
  }
};

const truncateContent = (content: string, length: number) => {
  return content.length > length ? content.substring(0, length) + '...' : content;
};

const formatDate = (date: string) => {
  return new Date(date).toLocaleString();
};

// 生命周期
onMounted(() => {
  fetchPosts();
  fetchMyPosts();
});
</script>
