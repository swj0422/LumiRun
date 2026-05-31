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
          <span v-if="!sidebarCollapsed" class="ml-2 text-lg font-bold text-gray-900 truncate">逐光成长系统</span>
        </div>
      </div>

      <!-- 导航菜单 -->
      <nav class="flex-1 py-4">
        <div class="space-y-1 px-2">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="flex items-center justify-center px-3 py-2 text-sm font-medium rounded-md"
            :class="
              isActive(item.path)
                ? 'text-primary-600 bg-primary-50 border-l-2 border-primary-600'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
            "
          >
            <svg class="w-5 h-5 flex-shrink-0" :class="sidebarCollapsed ? '' : 'mr-3'" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path v-if="item.name === '首页'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              <path v-else-if="item.name === '组织管理'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              <path v-else-if="item.name === '成员管理'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
              <path v-else-if="item.name === '成长管理'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              <path v-else-if="item.name === '奖励管理'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
              <path v-else-if="item.name === '兑换管理'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
              <path v-else-if="item.name === '标签管理'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
              <path v-else-if="item.name === '意见征集'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              <path v-else-if="item.name === '心愿便利贴'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            <span v-if="!sidebarCollapsed" class="truncate">{{ item.name }}</span>
          </router-link>
        </div>
      </nav>

      <!-- 用户信息和消息通知 -->
      <div class="px-3 py-3 border-t border-gray-200">
        <div v-if="!sidebarCollapsed" class="flex items-center justify-between mb-2">
          <span class="text-sm text-gray-700 truncate flex-1">{{ userStore.userInfo?.real_name }}</span>
          <button
            @click="toggleMessagePanel"
            class="relative p-1 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md"
            title="消息通知"
          >
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
            <span
              v-if="unreadCount > 0"
              class="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-4 w-4 flex items-center justify-center"
            >
              {{ unreadCount > 99 ? '99+' : unreadCount }}
            </span>
          </button>
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
            <span class="ml-2 text-xl font-bold text-gray-900">逐光成长系统</span>
          </router-link>
        </div>

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

      <div
        v-if="mobileMenuOpen"
        class="py-4 border-t border-gray-200 px-4"
      >
        <div class="space-y-2">
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
          <div class="pt-4 border-t border-gray-200">
            <div class="flex items-center justify-between">
              <span class="text-base font-medium text-gray-700">{{ userStore.userInfo?.real_name }}</span>
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
    </header>

    <!-- 消息面板 -->
    <div
      v-if="messagePanelOpen"
      class="fixed right-4 top-20 w-80 bg-white rounded-lg shadow-xl border border-gray-200 z-50 max-h-96 overflow-hidden"
    >
      <div class="flex items-center justify-between p-3 border-b border-gray-200">
        <h3 class="text-sm font-semibold text-gray-700">消息通知</h3>
        <button
          @click="messagePanelOpen = false"
          class="text-gray-400 hover:text-gray-600"
        >
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      <div class="overflow-y-auto max-h-72 p-2">
        <div v-if="messages.length === 0" class="text-center py-8 text-gray-400">
          暂无消息
        </div>
        <div
          v-for="msg in messages"
          :key="msg.id"
          class="p-2 rounded-md hover:bg-gray-50 cursor-pointer"
          :class="msg.is_read ? '' : 'bg-blue-50'"
          @click="markMessageRead(msg.id)"
        >
          <p class="text-sm text-gray-700">{{ msg.content }}</p>
          <p class="text-xs text-gray-400 mt-1">{{ formatTime(msg.created_at) }}</p>
        </div>
      </div>
    </div>

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
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();
const mobileMenuOpen = ref(false);
const sidebarCollapsed = ref(false);

// 消息相关状态
const messagePanelOpen = ref(false);
const unreadCount = ref(0);
const messages = ref<any[]>([]);
let messageRefreshTimer: number | null = null;

interface Message {
  id: number;
  user_id: number;
  content: string;
  type: number;
  is_read: boolean;
  created_at: string;
}

const toggleMessagePanel = async () => {
  messagePanelOpen.value = !messagePanelOpen.value;
  if (messagePanelOpen.value) {
    await fetchMessages();
  }
};

const fetchMessages = async () => {
  try {
    const response = await fetch('/api/v1/messages/list', {
      headers: {
        'Authorization': `Bearer ${userStore.token}`
      }
    });
    if (response.ok) {
      const data = await response.json();
      messages.value = data.items;
      updateUnreadCount();
    }
  } catch (error) {
    console.error('获取消息失败:', error);
  }
};

const fetchUnreadCount = async () => {
  try {
    const response = await fetch('/api/v1/messages/unread-count', {
      headers: {
        'Authorization': `Bearer ${userStore.token}`
      }
    });
    if (response.ok) {
      const data = await response.json();
      unreadCount.value = data.count;
    }
  } catch (error) {
    console.error('获取未读消息数量失败:', error);
  }
};

const updateUnreadCount = () => {
  unreadCount.value = messages.value.filter(msg => !msg.is_read).length;
};

const markMessageRead = async (messageId: number) => {
  try {
    const response = await fetch('/api/v1/messages/read', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${userStore.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ message_ids: [messageId] })
    });
    if (response.ok) {
      const msg = messages.value.find(m => m.id === messageId);
      if (msg) {
        msg.is_read = true;
        updateUnreadCount();
      }
    }
  } catch (error) {
    console.error('标记消息已读失败:', error);
  }
};

const formatTime = (dateString: string) => {
  const date = new Date(dateString);
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const minutes = Math.floor(diff / (1000 * 60));
  const hours = Math.floor(diff / (1000 * 60 * 60));
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));

  if (minutes < 1) return '刚刚';
  if (minutes < 60) return `${minutes}分钟前`;
  if (hours < 24) return `${hours}小时前`;
  if (days < 7) return `${days}天前`;
  return date.toLocaleDateString('zh-CN');
};

const startMessageRefresh = () => {
  messageRefreshTimer = window.setInterval(() => {
    fetchUnreadCount();
  }, 30000);
};

const stopMessageRefresh = () => {
  if (messageRefreshTimer) {
    clearInterval(messageRefreshTimer);
    messageRefreshTimer = null;
  }
};

onMounted(() => {
  fetchUnreadCount();
  startMessageRefresh();
});

onUnmounted(() => {
  stopMessageRefresh();
});

const navItems = computed(() => {
  const userRole = userStore.userInfo?.role_name;
  if (userRole === 'class_assistant') {
    return [
      { name: '首页', path: '/teacher' },
      { name: '组织管理', path: '/teacher/classes' },
      { name: '成员管理', path: '/teacher/students' },
      { name: '成长管理', path: '/teacher/growth' },
      { name: '意见征集', path: '/teacher/suggestion-forum' },
      { name: '心愿便利贴', path: '/teacher/wish-wall' },
    ];
  } else {
    return [
      { name: '首页', path: '/teacher' },
      { name: '组织管理', path: '/teacher/classes' },
      { name: '成员管理', path: '/teacher/students' },
      { name: '成长管理', path: '/teacher/growth' },
      { name: '奖励管理', path: '/teacher/rewards' },
      { name: '兑换管理', path: '/teacher/orders' },
      { name: '标签管理', path: '/teacher/tags' },
      { name: '意见征集', path: '/teacher/suggestion-forum' },
      { name: '心愿便利贴', path: '/teacher/wish-wall' },
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
