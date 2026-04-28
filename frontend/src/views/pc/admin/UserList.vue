<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-900">用户管理</h1>
      <button @click="showCreateModal = true" class="btn-primary">
        创建用户
      </button>
    </div>

    <!-- 创建用户弹窗 -->
    <div
      v-if="showCreateModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
        <h2 class="text-xl font-bold mb-4">创建用户</h2>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1"
              >真实姓名</label
            >
            <input
              v-model="createForm.real_name"
              type="text"
              class="input w-full"
              placeholder="请输入真实姓名"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1"
              >邮箱</label
            >
            <input
              v-model="createForm.email"
              type="email"
              class="input w-full"
              placeholder="请输入邮箱"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1"
              >密码</label
            >
            <input
              v-model="createForm.password"
              type="password"
              class="input w-full"
              placeholder="请输入密码（至少6位，包含大小写字母）"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1"
              >角色</label
            >
            <select v-model="createForm.role_id" class="input w-full">
              <option value="2">管理员</option>
              <option value="3">导师</option>
              <option value="4">学员</option>
            </select>
          </div>
          <div class="flex justify-end gap-2">
            <button @click="showCreateModal = false" class="btn-secondary">
              取消
            </button>
            <button @click="createUser" class="btn-primary">创建</button>
          </div>
        </div>
      </div>
    </div>

    <div class="bg-white rounded-lg shadow p-4">
      <div class="flex flex-wrap gap-4">
        <div class="flex-1 min-w-[200px]">
          <input
            v-model="searchKeyword"
            type="text"
            class="input"
            placeholder="搜索用户姓名或邮箱"
            @input="handleSearch"
          />
        </div>
        <select v-model="selectedRole" class="input w-48" @change="fetchUsers">
          <option value="">全部角色</option>
          <option value="1">超级管理员</option>
          <option value="2">管理员</option>
          <option value="3">导师</option>
          <option value="4">学员</option>
        </select>
        <select
          v-model="selectedStatus"
          class="input w-32"
          @change="fetchUsers"
        >
          <option value="">全部状态</option>
          <option value="true">启用</option>
          <option value="false">禁用</option>
        </select>
      </div>
    </div>

    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              用户
            </th>
            <th
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              角色
            </th>
            <th
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              状态
            </th>
            <th
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              注册时间
            </th>
            <th
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              操作
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="user in users" :key="user.id">
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="flex items-center">
                <div
                  class="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center"
                >
                  <span class="text-gray-600 font-medium">{{
                    user.real_name?.charAt(0)
                  }}</span>
                </div>
                <div class="ml-4">
                  <div class="text-sm font-medium text-gray-900">
                    {{ user.real_name }}
                  </div>
                  <div class="text-sm text-gray-500">{{ user.email }}</div>
                </div>
              </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span
                :class="getRoleClass(user.role_id)"
                class="px-2 py-1 text-xs rounded-full"
              >
                {{ user.role_name }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span
                :class="
                  user.status
                    ? 'bg-green-100 text-green-800'
                    : 'bg-red-100 text-red-800'
                "
                class="px-2 py-1 text-xs rounded-full"
              >
                {{ user.status ? '启用' : '禁用' }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ formatDate(user.created_at) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
              <!-- 超级管理员不能操作自己 -->
              <template
                v-if="user.role_id === 1 && user.id === userStore.userInfo?.id"
              >
                <span class="text-gray-400">无法操作</span>
              </template>
              <template v-else>
                <template v-if="!user.status && user.role_id === 3">
                  <button
                    @click="approveUser(user.id)"
                    class="text-green-600 hover:text-green-700 mr-2"
                  >
                    通过
                  </button>
                  <button
                    @click="rejectUser(user.id)"
                    class="text-red-600 hover:text-red-700 mr-2"
                  >
                    拒绝
                  </button>
                </template>
                <button
                  v-if="user.status"
                  @click="disableUser(user.id)"
                  class="text-red-600 hover:text-red-700"
                >
                  禁用
                </button>
                <button
                  v-else-if="user.role_id !== 3"
                  @click="enableUser(user.id)"
                  class="text-green-600 hover:text-green-700"
                >
                  启用
                </button>
              </template>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="users.length === 0" class="text-center py-12">
        <p class="text-gray-500">暂无用户数据</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import request from '@/api/request';
import { useUserStore } from '@/stores/user';
import { onMounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';

interface User {
  id: number;
  real_name: string;
  email: string;
  phone?: string;
  role_id: number;
  role_name: string;
  status: boolean;
  created_at: string;
}

const route = useRoute();
const userStore = useUserStore();

const users = ref<User[]>([]);
const searchKeyword = ref('');
const selectedRole = ref('');
const selectedStatus = ref('');
const showCreateModal = ref(false);

interface CreateForm {
  real_name: string;
  email: string;
  password: string;
  role_id: number;
}

const createForm = ref<CreateForm>({
  real_name: '',
  email: '',
  password: '',
  role_id: 2,
});

const fetchUsers = async () => {
  try {
    const params: Record<string, any> = {};
    if (selectedRole.value) {
      params.role_id = selectedRole.value;
    }
    if (selectedStatus.value) {
      params.status = selectedStatus.value === 'true';
    }
    if (searchKeyword.value) {
      params.keyword = searchKeyword.value;
    }
    const data = (await request.get('/v1/admin/users', { params })) as {
      items: User[];
    };
    users.value = data.items || [];
  } catch (error) {
    console.error('获取用户列表失败:', error);
  }
};

const handleSearch = () => {
  fetchUsers();
};

const approveUser = async (id: number) => {
  try {
    await request.post(`/v1/admin/users/${id}/approve`);
    fetchUsers();
  } catch (error) {
    console.error('审核失败:', error);
  }
};

const rejectUser = async (id: number) => {
  try {
    await request.post(`/v1/admin/users/${id}/reject`);
    fetchUsers();
  } catch (error) {
    console.error('拒绝失败:', error);
  }
};

const disableUser = async (id: number) => {
  try {
    await request.post(`/v1/admin/users/${id}/disable`);
    fetchUsers();
  } catch (error) {
    console.error('禁用用户失败:', error);
  }
};

const enableUser = async (id: number) => {
  try {
    await request.post(`/v1/admin/users/${id}/enable`);
    fetchUsers();
  } catch (error) {
    console.error('启用用户失败:', error);
  }
};

const createUser = async () => {
  try {
    await request.post('/v1/auth/register', {
      real_name: createForm.value.real_name,
      email: createForm.value.email,
      password: createForm.value.password,
      role_id: createForm.value.role_id,
    });
    showCreateModal.value = false;
    createForm.value = {
      real_name: '',
      email: '',
      password: '',
      role_id: 2,
    };
    fetchUsers();
  } catch (error) {
    console.error('创建用户失败:', error);
  }
};

const getRoleClass = (roleId: number) => {
  const classes: Record<number, string> = {
    1: 'bg-red-100 text-red-800',
    2: 'bg-purple-100 text-purple-800',
    3: 'bg-blue-100 text-blue-800',
    4: 'bg-green-100 text-green-800',
  };
  return classes[roleId] || 'bg-gray-100 text-gray-800';
};

const formatDate = (date: string) => {
  return new Date(date).toLocaleString('zh-CN');
};

watch(
  () => route.query,
  (query) => {
    if (query.role_id) {
      selectedRole.value = query.role_id as string;
    }
    if (query.status !== undefined) {
      selectedStatus.value = query.status as string;
    }
    fetchUsers();
  },
  { immediate: true }
);

onMounted(() => {
  const query = route.query;
  if (query.role_id) {
    selectedRole.value = query.role_id as string;
  }
  if (query.status !== undefined) {
    selectedStatus.value = query.status as string;
  }
  fetchUsers();
});
</script>
