<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 顶部导航栏 -->
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <!-- 第一行：Logo和用户信息 -->
        <div class="flex justify-between h-16">
          <!-- Logo -->
          <div class="flex items-center">
            <router-link to="/admin" class="flex items-center">
              <div
                class="w-8 h-8 bg-red-600 rounded-lg flex items-center justify-center"
              >
                <svg
                  class="w-5 h-5 text-white"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                  />
                </svg>
              </div>
              <span class="ml-2 text-xl font-bold text-gray-900"
                >逐光成长系统 - 管理后台</span
              >
            </router-link>
          </div>

          <!-- 移动端菜单按钮 -->
          <div class="md:hidden flex items-center">
            <button
              @click="mobileMenuOpen = !mobileMenuOpen"
              class="p-2 rounded-md text-gray-500 hover:text-gray-700 hover:bg-gray-100"
            >
              <svg
                class="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  v-if="!mobileMenuOpen"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M4 6h16M4 12h16M4 18h16"
                />
                <path
                  v-else
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>

          <!-- 用户信息 -->
          <div class="hidden md:flex items-center">
            <div class="flex items-center space-x-4">
              <span class="text-sm text-gray-700">{{
                userStore.userInfo?.real_name
              }}</span>
              <button
                @click="handleLogout"
                class="text-sm text-gray-500 hover:text-gray-700"
              >
                退出
              </button>
            </div>
          </div>
        </div>

        <!-- 第二行：导航菜单 -->
        <nav class="hidden md:flex space-x-8 h-12 items-center">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="inline-flex items-center px-1 pt-1 text-sm font-medium"
            :class="
              isActive(item.path)
                ? 'text-red-600 border-b-2 border-red-600'
                : 'text-gray-500 hover:text-gray-700'
            "
          >
            {{ item.name }}
          </router-link>
        </nav>

        <!-- 移动端导航菜单 -->
        <div
          v-if="mobileMenuOpen"
          class="md:hidden py-4 border-t border-gray-200"
        >
          <div class="space-y-4">
            <router-link
              v-for="item in navItems"
              :key="item.path"
              :to="item.path"
              @click="mobileMenuOpen = false"
              class="block px-3 py-2 rounded-md text-base font-medium"
              :class="
                isActive(item.path)
                  ? 'text-red-600 bg-red-50'
                  : 'text-gray-700 hover:text-gray-900 hover:bg-gray-50'
              "
            >
              {{ item.name }}
            </router-link>
            <div class="px-3 py-2">
              <div class="flex items-center justify-between">
                <span class="text-base font-medium text-gray-700">{{
                  userStore.userInfo?.real_name
                }}</span>
                <button
                  @click="handleLogout"
                  class="text-base font-medium text-gray-500 hover:text-gray-700"
                >
                  退出
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { useUserStore } from '@/stores/user';
import { ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();
const mobileMenuOpen = ref(false);

const navItems = [
  { name: '首页', path: '/admin' },
  { name: '用户管理', path: '/admin/users' },
  { name: '角色管理', path: '/admin/roles' },
  { name: '权限管理', path: '/admin/permissions' },
  { name: '系统日志', path: '/admin/logs' },
];

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
</script>
