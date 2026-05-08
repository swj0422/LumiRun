<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-900">角色管理</h1>
      <button @click="showCreateModal = true" class="btn-primary">创建角色</button>
    </div>

    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">角色名称</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">角色描述</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">菜单权限</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">按钮权限</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="role in roles" :key="role.id">
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ role.role_name }}</td>
            <td class="px-6 py-4 text-sm text-gray-500">{{ role.remark || '-' }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
              <span class="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs">{{ role.menu_count }} 个</span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
              <span class="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">{{ role.button_count }} 个</span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
              <template v-if="role.id <= 4">
                <button @click="openPermissionModal(role)" class="text-green-600 hover:text-green-700">权限</button>
              </template>
              <template v-else>
                <button @click="editRole(role)" class="text-blue-600 hover:text-blue-700 mr-2">编辑</button>
                <button @click="openPermissionModal(role)" class="text-green-600 hover:text-green-700 mr-2">权限</button>
                <button @click="deleteRole(role.id)" class="text-red-600 hover:text-red-700">删除</button>
              </template>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="roles.length === 0" class="text-center py-12">
        <p class="text-gray-500">暂无角色数据</p>
      </div>
    </div>

    <div v-if="showCreateModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
        <h2 class="text-xl font-bold mb-4">创建角色</h2>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">角色名称</label>
            <input v-model="createForm.role_name" type="text" class="input w-full" placeholder="请输入角色名称" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">角色描述</label>
            <textarea v-model="createForm.remark" class="input w-full" placeholder="请输入角色描述" rows="3"></textarea>
          </div>
          <div class="flex justify-end gap-2">
            <button @click="showCreateModal = false" class="btn-secondary">取消</button>
            <button @click="createRole" class="btn-primary">创建</button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showEditModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
        <h2 class="text-xl font-bold mb-4">编辑角色</h2>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">角色名称</label>
            <input v-model="editForm.role_name" type="text" class="input w-full" placeholder="请输入角色名称" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">角色描述</label>
            <textarea v-model="editForm.remark" class="input w-full" placeholder="请输入角色描述" rows="3"></textarea>
          </div>
          <div class="flex justify-end gap-2">
            <button @click="showEditModal = false" class="btn-secondary">取消</button>
            <button @click="updateRole" class="btn-primary">保存</button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showPermissionModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl p-6 w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        <h2 class="text-xl font-bold mb-4">分配权限 - {{ selectedRole?.role_name }}</h2>
        
        <div class="flex gap-4 mb-4">
          <button
            @click="activeTab = 'menu'"
            :class="activeTab === 'menu' ? 'bg-primary-500 text-white' : 'bg-gray-100 text-gray-700'"
            class="px-4 py-2 rounded-lg text-sm font-medium"
          >
            菜单权限 ({{ menuPermissions.length }})
          </button>
          <button
            @click="activeTab = 'button'"
            :class="activeTab === 'button' ? 'bg-primary-500 text-white' : 'bg-gray-100 text-gray-700'"
            class="px-4 py-2 rounded-lg text-sm font-medium"
          >
            按钮权限 ({{ buttonPermissions.length }})
          </button>
        </div>

        <div class="flex-1 overflow-y-auto">
          <div v-show="activeTab === 'menu'" class="space-y-2">
            <div class="flex items-center mb-4">
              <input
                type="checkbox"
                id="select-all-menu"
                :checked="isAllMenuSelected"
                @change="toggleAllMenu"
                class="mr-2"
              />
              <label for="select-all-menu" class="text-sm font-medium text-gray-700">全选菜单权限</label>
            </div>
            <div v-for="permission in menuPermissions" :key="permission.id" class="flex items-center py-2 border-b border-gray-100">
              <input
                type="checkbox"
                :id="`menu-${permission.id}`"
                :checked="selectedPermissions.includes(permission.id)"
                @change="handlePermissionChange(permission.id)"
                class="mr-3"
              />
              <label :for="`menu-${permission.id}`" class="flex-1">
                <span class="text-sm font-medium text-gray-900">{{ permission.permission_name }}</span>
                <span class="text-xs text-gray-500 ml-2">{{ permission.path }}</span>
              </label>
            </div>
          </div>

          <div v-show="activeTab === 'button'" class="space-y-2">
            <div class="flex items-center mb-4">
              <input
                type="checkbox"
                id="select-all-button"
                :checked="isAllButtonSelected"
                @change="toggleAllButton"
                class="mr-2"
              />
              <label for="select-all-button" class="text-sm font-medium text-gray-700">全选按钮权限</label>
            </div>
            <div v-for="permission in buttonPermissions" :key="permission.id" class="flex items-center py-2 border-b border-gray-100">
              <input
                type="checkbox"
                :id="`button-${permission.id}`"
                :checked="selectedPermissions.includes(permission.id)"
                @change="handlePermissionChange(permission.id)"
                class="mr-3"
              />
              <label :for="`button-${permission.id}`" class="flex-1">
                <span class="text-sm font-medium text-gray-900">{{ permission.permission_name }}</span>
                <span class="text-xs text-gray-500 ml-2">{{ permission.permission_code }}</span>
              </label>
            </div>
          </div>
        </div>

        <div class="flex justify-end gap-2 mt-4 pt-4 border-t">
          <button @click="showPermissionModal = false" class="btn-secondary">取消</button>
          <button @click="assignPermissions" class="btn-primary">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import request from '@/api/request';
import { onMounted, ref, computed } from 'vue';

interface Role {
  id: number;
  role_name: string;
  remark: string;
  menu_count: number;
  button_count: number;
}

interface Permission {
  id: number;
  permission_name: string;
  permission_code: string;
  parent_id: number | null;
  type: number;
  path: string | null;
}

const roles = ref<Role[]>([]);
const menuPermissions = ref<Permission[]>([]);
const buttonPermissions = ref<Permission[]>([]);
const showCreateModal = ref(false);
const showEditModal = ref(false);
const showPermissionModal = ref(false);
const selectedRoleId = ref<number | null>(null);
const selectedRole = ref<Role | null>(null);
const selectedPermissions = ref<number[]>([]);
const activeTab = ref<'menu' | 'button'>('menu');

const createForm = ref({ role_name: '', remark: '' });
const editForm = ref({ id: 0, role_name: '', remark: '' });

const isAllMenuSelected = computed(() => {
  if (menuPermissions.value.length === 0) return false;
  return menuPermissions.value.every(p => selectedPermissions.value.includes(p.id));
});

const isAllButtonSelected = computed(() => {
  if (buttonPermissions.value.length === 0) return false;
  return buttonPermissions.value.every(p => selectedPermissions.value.includes(p.id));
});

const fetchRoles = async () => {
  try {
    const data = (await request.get('/api/v1/role/roles')) as { items: Role[] };
    roles.value = data.items || [];
  } catch (error) {
    console.error('获取角色列表失败:', error);
  }
};

const fetchPermissions = async () => {
  try {
    const data = (await request.get('/api/v1/role/permissions')) as {
      menu_permissions: Permission[];
      button_permissions: Permission[];
    };
    menuPermissions.value = data.menu_permissions || [];
    buttonPermissions.value = data.button_permissions || [];
  } catch (error) {
    console.error('获取权限列表失败:', error);
  }
};

const createRole = async () => {
  try {
    await request.post('/api/v1/role/roles', createForm.value);
    showCreateModal.value = false;
    createForm.value = { role_name: '', remark: '' };
    fetchRoles();
  } catch (error) {
    console.error('创建角色失败:', error);
  }
};

const editRole = (role: Role) => {
  editForm.value = { id: role.id, role_name: role.role_name, remark: role.remark };
  showEditModal.value = true;
};

const updateRole = async () => {
  try {
    await request.put(`/api/v1/role/roles/${editForm.value.id}`, {
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
  if (!confirm('确定要删除这个角色吗？')) return;
  try {
    await request.delete(`/api/v1/role/roles/${id}`);
    fetchRoles();
  } catch (error) {
    console.error('删除角色失败:', error);
  }
};

const openPermissionModal = async (role: Role) => {
  selectedRoleId.value = role.id;
  selectedRole.value = role;
  try {
    const data = (await request.get(`/api/v1/role/roles/${role.id}/permissions`)) as { permission_ids: number[] };
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

const toggleAllMenu = () => {
  const menuIds = menuPermissions.value.map(p => p.id);
  if (isAllMenuSelected.value) {
    selectedPermissions.value = selectedPermissions.value.filter(id => !menuIds.includes(id));
  } else {
    const newIds = menuIds.filter(id => !selectedPermissions.value.includes(id));
    selectedPermissions.value.push(...newIds);
  }
};

const toggleAllButton = () => {
  const buttonIds = buttonPermissions.value.map(p => p.id);
  if (isAllButtonSelected.value) {
    selectedPermissions.value = selectedPermissions.value.filter(id => !buttonIds.includes(id));
  } else {
    const newIds = buttonIds.filter(id => !selectedPermissions.value.includes(id));
    selectedPermissions.value.push(...newIds);
  }
};

const assignPermissions = async () => {
  if (selectedRoleId.value) {
    try {
      await request.post(`/api/v1/role/roles/${selectedRoleId.value}/permissions`, {
        permission_ids: selectedPermissions.value,
      });
      showPermissionModal.value = false;
      fetchRoles();
    } catch (error) {
      console.error('分配权限失败:', error);
    }
  }
};

onMounted(() => {
  fetchRoles();
});
</script>
