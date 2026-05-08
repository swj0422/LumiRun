<template>
  <div class="min-h-screen bg-gray-50 flex">
    <!-- 侧边栏导航 -->
    <aside
      :class="[
        'hidden md:flex flex-col bg-white border-r border-gray-200 fixed left-0 top-0 h-screen transition-all duration-300 z-40',
        sidebarCollapsed ? 'w-16' : 'w-56'
      ]"
    >
      <!-- Logo区域 -->
      <div class="flex items-center h-16 px-4 border-b border-gray-200">
        <div class="flex items-center flex-1 cursor-pointer" @click.stop="sidebarCollapsed = !sidebarCollapsed">
          <div class="w-8 h-8 bg-red-600 rounded-lg flex items-center justify-center">
            <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          <span v-if="!sidebarCollapsed" class="ml-2 text-lg font-bold text-gray-900 truncate">逐光成长系统</span>
        </div>
      </div>

      <!-- 导航菜单 -->
      <nav class="flex-1 py-4">
        <div class="space-y-1 px-2">
          <router-link
            v-for="item in visibleNavItems"
            :key="item.path"
            :to="item.path"
            class="flex items-center justify-center px-3 py-2 text-sm font-medium rounded-md"
            :class="isActive(item.path) ? 'text-red-600 bg-red-50 border-l-2 border-red-600' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'"
          >
            <svg class="w-5 h-5 flex-shrink-0" :class="sidebarCollapsed ? '' : 'mr-3'" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path v-if="item.name === '控制台'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              <path v-else-if="item.name === '用户管理'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
              <path v-else-if="item.name === '角色管理'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path v-else-if="item.name === '权限管理'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              <path v-else-if="item.name === '班级管理'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              <path v-else-if="item.name === '学员管理'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              <path v-else-if="item.name === '礼品管理'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
              <path v-else-if="item.name === '订单管理'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              <path v-else-if="item.name === '心愿便利贴'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              <path v-else-if="item.name === '意见征集'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              <path v-else-if="item.name === '系统日志'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              <path v-else-if="item.name === '系统设置'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            <span v-if="!sidebarCollapsed" class="truncate">{{ item.name }}</span>
          </router-link>
        </div>
      </nav>

      <!-- 用户信息和退出 -->
      <div class="px-3 py-3 border-t border-gray-200">
        <div v-if="!sidebarCollapsed" class="flex items-center justify-between mb-2">
          <span class="text-sm text-gray-700 truncate flex-1">{{ userStore.userInfo?.real_name }}</span>
          <span class="text-xs text-gray-400 ml-2">{{ getRoleName(userStore.userInfo?.role_id) }}</span>
        </div>
        <div class="flex items-center justify-between">
          <button
            v-if="!sidebarCollapsed"
            @click="handleLogout"
            class="text-sm text-gray-500 hover:text-gray-700"
          >
            退出
          </button>
          <button
            v-else
            @click="handleLogout"
            class="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md"
            title="退出"
          >
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
          </button>
        </div>
      </div>
    </aside>

    <!-- 移动端顶部导航栏 -->
    <header class="md:hidden bg-white shadow-sm border-b border-gray-200 fixed top-0 left-0 right-0 z-50">
      <div class="flex justify-between h-16 px-4">
        <div class="flex items-center">
          <router-link to="/admin" class="flex items-center">
            <div class="w-8 h-8 bg-red-600 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <span class="ml-2 text-xl font-bold text-gray-900">逐光成长系统</span>
          </router-link>
        </div>

        <button @click="mobileMenuOpen = !mobileMenuOpen" class="p-2 rounded-md text-gray-500 hover:text-gray-700 hover:bg-gray-100">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path v-if="!mobileMenuOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div v-if="mobileMenuOpen" class="py-4 border-t border-gray-200 px-4">
        <div class="space-y-2">
          <router-link
            v-for="item in visibleNavItems"
            :key="item.path"
            :to="item.path"
            @click="mobileMenuOpen = false"
            class="block px-3 py-2 rounded-md text-base font-medium"
            :class="isActive(item.path) ? 'text-red-600 bg-red-50' : 'text-gray-700 hover:text-gray-900 hover:bg-gray-50'"
          >
            {{ item.name }}
          </router-link>
          <div class="pt-4 border-t border-gray-200">
            <div class="flex items-center justify-between">
              <div>
                <span class="text-base font-medium text-gray-700">{{ userStore.userInfo?.real_name }}</span>
                <span class="text-xs text-gray-400 ml-2">{{ getRoleName(userStore.userInfo?.role_id) }}</span>
              </div>
              <button @click="handleLogout" class="text-base font-medium text-gray-500 hover:text-gray-700">退出</button>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- 主内容区 -->
    <main :class="['flex-1 transition-all duration-300', sidebarCollapsed ? 'md:ml-16' : 'md:ml-56']">
      <div class="max-w-6xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { useUserStore } from '@/stores/user';
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import request from '@/api/request';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();
const mobileMenuOpen = ref(false);
const sidebarCollapsed = ref(false);
const userPermissions = ref<string[]>([]);

const allNavItems = [
  { name: '控制台', path: '/admin', permission: 'menu:dashboard' },
  { name: '用户管理', path: '/admin/users', permission: 'menu:user' },
  { name: '角色管理', path: '/admin/roles', permission: 'menu:role' },
  { name: '权限管理', path: '/admin/permissions', permission: 'menu:permission' },
  { name: '班级管理', path: '/admin/classes', permission: 'menu:class' },
  { name: '学员管理', path: '/admin/students', permission: 'menu:student' },
  { name: '礼品管理', path: '/admin/gifts', permission: 'menu:gift' },
  { name: '订单管理', path: '/admin/orders', permission: 'menu:order' },
  { name: '心愿便利贴', path: '/admin/wishes', permission: 'menu:wish' },
  { name: '意见征集', path: '/admin/suggestions', permission: 'menu:suggestion' },
  { name: '系统日志', path: '/admin/logs', permission: 'menu:log' },
  { name: '系统设置', path: '/admin/settings', permission: 'menu:settings' },
];

const visibleNavItems = computed(() => {
  if (userPermissions.value.length === 0) {
    return allNavItems.filter(item => 
      userStore.userInfo?.role_id === 1 || 
      ['menu:dashboard', 'menu:user', 'menu:class', 'menu:student', 'menu:gift', 'menu:order', 'menu:wish', 'menu:suggestion', 'menu:log'].includes(item.permission)
    );
  }
  return allNavItems.filter(item => userPermissions.value.includes(item.permission));
});

const isActive = (path: string) => {
  if (path === '/admin') {
    return route.path === '/admin';
  }
  return route.path === path || route.path.startsWith(path + '/');
};

const handleLogout = () => {
  userStore.logout();
  router.push('/login');
};

const getRoleName = (roleId: number | undefined): string => {
  const roleNames: Record<number, string> = {
    1: '超级管理员',
    2: '管理员',
    3: '导师',
    4: '学员',
  };
  return roleNames[roleId || 0] || '未知';
};

const fetchUserPermissions = async () => {
  try {
    const data = (await request.get('/api/v1/user/permissions')) as { permissions: string[] };
    userPermissions.value = data.permissions || [];
  } catch (error) {
    console.error('获取用户权限失败:', error);
  }
};

onMounted(() => {
  fetchUserPermissions();
});
</script>
