<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-900">权限管理</h1>
    </div>

    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              权限名称
            </th>
            <th
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              权限编码
            </th>
            <th
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              权限类型
            </th>
            <th
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              路由路径
            </th>
            <th
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              状态
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="permission in permissions" :key="permission.id">
            <td
              class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900"
            >
              {{ permission.permission_name }}
            </td>
            <td class="px-6 py-4 text-sm text-gray-500">
              {{ permission.permission_code }}
            </td>
            <td class="px-6 py-4 text-sm text-gray-500">
              {{ permission.type === 1 ? '菜单' : '按钮' }}
            </td>
            <td class="px-6 py-4 text-sm text-gray-500">
              {{ permission.path || '-' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span
                :class="
                  permission.status
                    ? 'bg-green-100 text-green-800'
                    : 'bg-red-100 text-red-800'
                "
                class="px-2 py-1 text-xs rounded-full"
              >
                {{ permission.status ? '启用' : '禁用' }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="permissions.length === 0" class="text-center py-12">
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

const permissions = ref<Permission[]>([]);

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

onMounted(() => {
  fetchPermissions();
});
</script>
