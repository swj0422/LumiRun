<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-900">权限管理</h1>
      <div class="text-sm text-gray-500">
        共 {{ menuPermissions.length + buttonPermissions.length }} 项权限
      </div>
    </div>

    <div class="flex gap-4 mb-4">
      <button
        @click="activeTab = 'menu'"
        :class="activeTab === 'menu' ? 'bg-primary-500 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'"
        class="px-6 py-2 rounded-lg text-sm font-medium shadow"
      >
        菜单权限 ({{ menuPermissions.length }})
      </button>
      <button
        @click="activeTab = 'button'"
        :class="activeTab === 'button' ? 'bg-primary-500 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'"
        class="px-6 py-2 rounded-lg text-sm font-medium shadow"
      >
        按钮权限 ({{ buttonPermissions.length }})
      </button>
    </div>

    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">权限名称</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">权限编码</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              {{ activeTab === 'menu' ? '路由路径' : '所属菜单' }}
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <template v-if="activeTab === 'menu'">
            <tr v-for="permission in menuPermissions" :key="permission.id">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ permission.id }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                {{ permission.permission_name }}
              </td>
              <td class="px-6 py-4 text-sm text-gray-500 font-mono text-xs">{{ permission.permission_code }}</td>
              <td class="px-6 py-4 text-sm text-gray-500">{{ permission.path || '-' }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="permission.status ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'" class="px-2 py-1 text-xs rounded-full">
                  {{ permission.status ? '启用' : '禁用' }}
                </span>
              </td>
            </tr>
          </template>
          <template v-else>
            <tr v-for="permission in buttonPermissions" :key="permission.id">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ permission.id }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                {{ permission.permission_name }}
              </td>
              <td class="px-6 py-4 text-sm text-gray-500 font-mono text-xs">{{ permission.permission_code }}</td>
              <td class="px-6 py-4 text-sm text-gray-500">{{ getParentMenuName(permission.parent_id) }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="permission.status ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'" class="px-2 py-1 text-xs rounded-full">
                  {{ permission.status ? '启用' : '禁用' }}
                </span>
              </td>
            </tr>
          </template>
        </tbody>
      </table>

      <div v-if="(activeTab === 'menu' ? menuPermissions : buttonPermissions).length === 0" class="text-center py-12">
        <p class="text-gray-500">暂无权限数据</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import request from '@/api/request';
import { onMounted, ref } from 'vue';

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

const menuPermissions = ref<Permission[]>([]);
const buttonPermissions = ref<Permission[]>([]);
const activeTab = ref<'menu' | 'button'>('menu');

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

const getParentMenuName = (parentId: number | null): string => {
  if (!parentId) return '-';
  const parent = menuPermissions.value.find(p => p.id === parentId);
  return parent ? parent.permission_name : '-';
};

onMounted(() => {
  fetchPermissions();
});
</script>
