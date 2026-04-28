import { computed } from 'vue';
import { useUserStore } from '@/stores/user';
import { isLoggedIn } from '@/utils';

export function useAuth() {
  const userStore = useUserStore();

  const isAuthenticated = computed(() => {
    return isLoggedIn() && userStore.userInfo !== null;
  });

  const userRole = computed(() => {
    return userStore.userInfo?.role_name || '';
  });

  const userInfo = computed(() => {
    return userStore.userInfo;
  });

  const login = async (email: string, password: string) => {
    try {
      await userStore.login(email, password);
      return true;
    } catch (error) {
      return false;
    }
  };

  const logout = async () => {
    await userStore.logout();
  };

  const refreshUserInfo = async () => {
    try {
      await userStore.fetchUserInfo();
      return true;
    } catch (error) {
      return false;
    }
  };

  const hasRole = (roles: string | string[]) => {
    const currentRole = userRole.value;
    if (Array.isArray(roles)) {
      return roles.includes(currentRole);
    }
    return currentRole === roles;
  };

  return {
    isAuthenticated,
    userRole,
    userInfo,
    login,
    logout,
    refreshUserInfo,
    hasRole,
  };
}
