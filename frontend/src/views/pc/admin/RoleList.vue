<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-900">角色管理</h1>
      <button @click="showCreateModal = true" class="btn-primary">
        创建角色
      </button>
    </div>

    <!-- 创建角色弹窗 -->
    <div
      v-if="showCreateModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
        <h2 class="text-xl font-bold mb-4">创建角色</h2>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1"
              >角色名称</label
            >
            <input
              v-model="createForm.role_name"
              type="text"
              class="input w-full"
              placeholder="请输入角色名称"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1"
              >角色描述</label
            >
            <textarea
              v-model="createForm.remark"
              class="input w-full"
              placeholder="请输入角色描述"
              rows="3"
            ></textarea>
          </div>
          <div class="flex justify-end gap-2">
            <button @click="showCreateModal = false" class="btn-secondary">
              取消
            </button>
            <button @click="createRole" class="btn-primary">创建</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 编辑角色弹窗 -->
    <div
      v-if="showEditModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
        <h2 class="text-xl font-bold mb-4">编辑角色</h2>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1"
              >角色名称</label
            >
            <input
              v-model="editForm.role_name"
              type="text"
              class="input w-full"
              placeholder="请输入角色名称"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1"
              >角色描述</label
            >
            <textarea
              v-model="editForm.remark"
              class="input w-full"
              placeholder="请输入角色描述"
              rows="3"
            ></textarea>
          </div>
          <div class="flex justify-end gap-2">
            <button @click="showEditModal = false" class="btn-secondary">
              取消
            </button>
            <button @click="updateRole" class="btn-primary">保存</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 权限分配弹窗 -->
    <div
      v-if="showPermissionModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg shadow-xl p-6 w-full max-w-2xl">
        <h2 class="text-xl font-bold mb-4">分配权限</h2>
        <div class="space-y-4">
          <div class="max-h-96 overflow-y-auto">
            <div
              v-for="permission in permissions"
              :key="permission.id"
              class="flex items-center mb-2"
            >
              <input
                type="checkbox"
                :id="`permission-${permission.id}`"
                :checked="selectedPermissions.includes(permission.id)"
                @change="handlePermissionChange(permission.id)"
                class="mr-2"
              />
              <label :for="`permission-${permission.id}`">{{
                permission.permission_name
              }}</label>
            </div>
          </div>
          <div class="flex justify-end gap-2">
            <button @click="showPermissionModal = false" class="btn-secondary">
              取消
            </button>
            <button @click="assignPermissions" class="btn-primary">保存</button>
          </div>
        </div>
      </div>
    </div>

    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              角色名称
            </th>
            <th
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              角色描述
            </th>
            <th
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              操作
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="role in roles" :key="role.id">
            <td
              class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900"
            >
              {{ role.role_name }}
            </td>
            <td class="px-6 py-4 text-sm text-gray-500">
              {{ role.remark || '-' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
              <!-- 系统默认角色不显示编辑和删除按钮 -->
              <template v-if="role.id <= 4">
                <button
                  @click="openPermissionModal(role)"
                  class="text-green-600 hover:text-green-700"
                >
                  权限
                </button>
              </template>
              <template v-else>
                <button
                  @click="editRole(role)"
                  class="text-blue-600 hover:text-blue-700 mr-2"
                >
                  编辑
                </button>
                <button
                  @click="openPermissionModal(role)"
                  class="text-green-600 hover:text-green-700 mr-2"
                >
                  权限
                </button>
                <button
                  @click="deleteRole(role.id)"
                  class="text-red-600 hover:text-red-700"
                >
                  删除
                </button>
              </template>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="roles.length === 0" class="text-center py-12">
        <p class="text-gray-500">暂无角色数据</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import request from '@/api/request';
import { onMounted, ref } from 'vue';

interface Role {
  id: number;
  role_name: string;
  remark: string;
}

interface Permission {
  id: number;
  permission_name: string;
  permission_code: string;
  parent_id: number | null;
  type: number;
  path: string | null;
  component: string | null;
  icon: string | null;
  sort: number;
  status: boolean;
}

const roles = ref<Role[]>([]);
const permissions = ref<Permission[]>([]);
const showCreateModal = ref(false);
const showEditModal = ref(false);
const showPermissionModal = ref(false);
const selectedRoleId = ref<number | null>(null);
const selectedPermissions = ref<number[]>([]);

const createForm = ref({
  role_name: '',
  remark: '',
});

const editForm = ref({
  id: 0,
  role_name: '',
  remark: '',
});

const fetchRoles = async () => {
  try {
    const data = (await request.get('/v1/role/roles')) as { items: Role[] };
    roles.value = data.items || [];
  } catch (error) {
    console.error('获取角色列表失败:', error);
  }
};

const fetchPermissions = async () => {
  try {
    const data = (await request.get('/v1/role/permissions')) as {
      items: Permission[];
    };
    permissions.value = data.items || [];
  } catch (error) {
    console.error('获取权限列表失败:', error);
  }
};

const createRole = async () => {
  try {
    await request.post('/v1/role/roles', createForm.value);
    showCreateModal.value = false;
    createForm.value = {
      role_name: '',
      remark: '',
    };
    fetchRoles();
  } catch (error) {
    console.error('创建角色失败:', error);
  }
};

const editRole = (role: Role) => {
  editForm.value = {
    id: role.id,
    role_name: role.role_name,
    remark: role.remark,
  };
  showEditModal.value = true;
};

const updateRole = async () => {
  try {
    await request.put(`/v1/role/roles/${editForm.value.id}`, {
      role_name: editForm.value.role_name,
      remark: editForm.value.remark,
    });
    showEditModal.value = false;
    fetchRoles();
  } catch (error) {
    console.error('更新角色失败:', error);
  }
};

const deleteRole = async (id: number) => {
  if (confirm('确定要删除这个角色吗？')) {
    try {
      await request.delete(`/v1/role/roles/${id}`);
      fetchRoles();
    } catch (error) {
      console.error('删除角色失败:', error);
    }
  }
};

const openPermissionModal = async (role: Role) => {
  selectedRoleId.value = role.id;
  try {
    const data = (await request.get(
      `/v1/role/roles/${role.id}/permissions`
    )) as { permission_ids: number[] };
    selectedPermissions.value = data.permission_ids || [];
    await fetchPermissions();
    showPermissionModal.value = true;
  } catch (error) {
    console.error('获取角色权限失败:', error);
  }
};

const handlePermissionChange = (permissionId: number) => {
  const index = selectedPermissions.value.indexOf(permissionId);
  if (index > -1) {
    selectedPermissions.value.splice(index, 1);
  } else {
    selectedPermissions.value.push(permissionId);
  }
};

const assignPermissions = async () => {
  if (selectedRoleId.value) {
    try {
      await request.post(
        `/v1/role/roles/${selectedRoleId.value}/permissions`,
        selectedPermissions.value
      );
      showPermissionModal.value = false;
    } catch (error) {
      console.error('分配权限失败:', error);
    }
  }
};

onMounted(() => {
  fetchRoles();
});
</script>
