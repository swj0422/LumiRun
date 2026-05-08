import { ref, onMounted } from 'vue';
import request from '@/api/request';

const userPermissions = ref<string[]>([]);

export function usePermission() {
  const fetchPermissions = async () => {
    try {
      const data = (await request.get('/api/v1/user/permissions')) as { permissions: string[] };
      userPermissions.value = data.permissions || [];
    } catch (error) {
      console.error('获取用户权限失败:', error);
    }
  };

  const hasPermission = (permission: string): boolean => {
    return userPermissions.value.includes(permission);
  };

  const hasAnyPermission = (permissions: string[]): boolean => {
    return permissions.some(p => userPermissions.value.includes(p));
  };

  const hasAllPermissions = (permissions: string[]): boolean => {
    return permissions.every(p => userPermissions.value.includes(p));
  };

  onMounted(() => {
    if (userPermissions.value.length === 0) {
      fetchPermissions();
    }
  });

  return {
    userPermissions,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    fetchPermissions,
  };
}

export function setupGlobalPermission() {
  const fetchPermissions = async () => {
    try {
      const data = (await request.get('/api/v1/user/permissions')) as { permissions: string[] };
      userPermissions.value = data.permissions || [];
    } catch (error) {
      console.error('获取用户权限失败:', error);
    }
  };

  fetchPermissions();

  return {
    userPermissions,
    hasPermission: (permission: string) => userPermissions.value.includes(permission),
    hasAnyPermission: (permissions: string[]) => permissions.some(p => userPermissions.value.includes(p)),
    hasAllPermissions: (permissions: string[]) => permissions.every(p => userPermissions.value.includes(p)),
  };
}

export { userPermissions };
