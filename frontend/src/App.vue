<template>
  <router-view />
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useUserStore } from '@/stores/user';

const userStore = useUserStore();

onMounted(async () => {
  // 如果有token但没有用户信息，尝试获取用户信息
  if (userStore.token && !userStore.userInfo) {
    try {
      await userStore.fetchUserInfo();
    } catch (error) {
      console.error('获取用户信息失败:', error);
    }
  }
});
</script>

<style>
/* 全局样式已在 index.css 中定义 */
</style>
