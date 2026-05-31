<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-primary-100 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div class="text-center">
        <div
          class="mx-auto h-16 w-16 bg-primary-600 rounded-full flex items-center justify-center"
        >
          <svg
            class="h-8 w-8 text-white"
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
        <h2 class="mt-6 text-3xl font-extrabold text-gray-900">角色选择</h2>
        <p class="mt-2 text-sm text-gray-600">
          请选择您要使用的身份
        </p>
      </div>

      <div class="card p-8 space-y-4">
        <div
          v-if="hasStudentRole"
          @click="selectRole('student')"
          class="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
        >
          <h3 class="text-lg font-semibold text-gray-900">成员身份</h3>
          <p class="text-sm text-gray-500">进入成员首页，查看个人成长记录</p>
        </div>

        <div
          v-if="hasAssistantRole"
          @click="selectRole('class_assistant')"
          class="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
        >
          <h3 class="text-lg font-semibold text-gray-900">组织助理身份</h3>
          <p class="text-sm text-gray-500">进入助理工作台，管理授权组织</p>
        </div>
      </div>

      <div class="text-center text-xs text-gray-500">
        <p>Lesimple System</p>
        <p class="mt-1">欢迎关注公众号繁乐简</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { checkUserAssistantStatus } from '@/api/class';
import request from '@/api/request';

const router = useRouter();

const hasStudentRole = ref(false);
const hasAssistantRole = ref(false);

// 从localStorage获取缓存的用户信息
function getCache(key: string) {
  try {
    const value = localStorage.getItem(key);
    return value ? JSON.parse(value) : null;
  } catch {
    return null;
  }
}

const checkRoles = async () => {
  try {
    console.log('[DEBUG] checkRoles 开始检查角色');
    // 直接从localStorage检查是否有助理授权
    const isClassAssistant = localStorage.getItem('isClassAssistant') === 'true';
    const assistantClassesStr = localStorage.getItem('assistantClasses');
    const assistantClasses = assistantClassesStr ? JSON.parse(assistantClassesStr) : [];
    hasAssistantRole.value = isClassAssistant && assistantClasses.length > 0;
    console.log('[DEBUG] checkRoles 助理状态:', { isClassAssistant, assistantClassesLength: assistantClasses.length, hasAssistantRole: hasAssistantRole.value });
    
    // 检查用户是否有成员角色
    // 1. 直接从用户信息判断角色
    const userInfo = getCache('userInfo');
    const isStudentRole = userInfo && userInfo.role_name === 'student';
    console.log('[DEBUG] checkRoles 用户信息:', userInfo, 'isStudentRole:', isStudentRole);
    
    // 2. 检查是否有绑定的组织
    let hasBoundClasses = false;
    try {
      const studentStatus = await request.get('/api/v1/students/my-classes');
      console.log('[DEBUG] checkRoles 成员状态响应:', studentStatus);
      hasBoundClasses = (studentStatus && Array.isArray(studentStatus) && studentStatus.length > 0) || false;
      console.log('[DEBUG] checkRoles hasBoundClasses:', hasBoundClasses);
    } catch (error) {
      console.error('检查成员状态失败:', error);
    }
    
    // 如果是student角色或者有绑定的组织，就显示成员身份选项
    hasStudentRole.value = isStudentRole || hasBoundClasses;
    console.log('[DEBUG] checkRoles 最终结果:', { hasStudentRole: hasStudentRole.value, hasAssistantRole: hasAssistantRole.value });
  } catch (error) {
    console.error('检查角色失败:', error);
  }
};

const selectRole = (role: string) => {
  // 保存用户选择的角色
  localStorage.setItem('selectedRole', role);
  
  // 根据选择的角色跳转到相应页面
  if (role === 'student') {
    router.push('/student');
  } else if (role === 'class_assistant') {
    router.push('/assistant');
  }
};

onMounted(async () => {
  await checkRoles();
});
</script>
