<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 顶部导航栏 -->
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <!-- 第一行：Logo和用户信息 -->
        <div class="flex justify-between h-16">
          <!-- Logo -->
          <div class="flex items-center">
            <router-link to="/teacher" class="flex items-center">
              <div
                class="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center"
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
                    d="M13 10V3L4 14h7v7l9-11h-7z"
                  />
                </svg>
              </div>
              <span class="ml-2 text-xl font-bold text-gray-900"
                >逐光成长系统</span
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
                ? 'text-primary-600 border-b-2 border-primary-600'
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
                  ? 'text-primary-600 bg-primary-50'
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
import { ref, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();
const mobileMenuOpen = ref(false);

const navItems = computed(() => {
  const userRole = userStore.userInfo?.role_name;
  if (userRole === 'class_assistant') {
    // 班级助理的菜单
    return [
      { name: '首页', path: '/teacher' },
      { name: '班级管理', path: '/teacher/classes' },
      { name: '学员管理', path: '/teacher/students' },
      { name: '成长管理', path: '/teacher/growth' },
      { name: '意见征集', path: '/teacher/suggestion-forum' },
    ];
  } else {
    // 导师的菜单
    return [
      { name: '首页', path: '/teacher' },
      { name: '班级管理', path: '/teacher/classes' },
      { name: '学员管理', path: '/teacher/students' },
      { name: '成长管理', path: '/teacher/growth' },
      { name: '奖励管理', path: '/teacher/rewards' },
      { name: '兑换管理', path: '/teacher/orders' },
      { name: '标签管理', path: '/teacher/tags' },
      { name: '意见征集', path: '/teacher/suggestion-forum' },
    ];
  }
});

const isActive = (path: string) => {
  if (path === '/teacher') {
    return route.path === '/teacher';
  }
  return route.path === path || route.path.startsWith(path + '/');
};

const handleLogout = () => {
  userStore.logout();
  router.push('/login');
};
</script>
