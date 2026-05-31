<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-900">组织管理</h1>
      <button v-if="!isClassAssistant" @click="showCreateModal = true" class="btn-primary">
        创建组织
      </button>
    </div>

    <!-- 组织列表 -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="classItem in classes"
        :key="classItem.id"
        class="bg-white rounded-lg shadow p-6"
      >
        <div class="flex justify-between items-start mb-4">
          <div>
            <h3 class="text-lg font-semibold text-gray-900">
              {{ classItem.session }}级 {{ classItem.class_name }}班
            </h3>
            <p class="text-sm text-gray-500">{{ classItem.school_name }}</p>
          </div>
          <div v-if="!isClassAssistant" class="flex items-center">
            <span class="text-xs text-gray-600 mr-2">{{
              classItem.status ? '正常' : '已关闭'
            }}</span>
            <label class="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                :checked="classItem.status"
                @change="toggleStatus(classItem)"
                class="sr-only peer"
              />
              <div
                class="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-500"
              ></div>
            </label>
          </div>
          <div v-else class="flex items-center">
            <span class="text-xs text-gray-600">{{
              classItem.status ? '正常' : '已关闭'
            }}</span>
          </div>
        </div>
        <div class="flex justify-between items-center text-sm text-gray-500">
          <span>成员数: {{ classItem.student_count || 0 }}</span>
          <div class="space-x-2">
            <button
              v-if="!isClassAssistant"
              @click="deleteClass(classItem)"
              class="text-red-600 hover:text-red-700"
            >
              删除
            </button>
            <button
              v-if="!isClassAssistant"
              @click="editClass(classItem)"
              class="text-primary-600 hover:text-primary-700"
            >
              编辑
            </button>
            <button
              @click="viewClass(classItem)"
              class="text-primary-600 hover:text-primary-700"
            >
              查看
            </button>
            <button
              @click="manageStudents(classItem)"
              class="text-primary-600 hover:text-primary-700"
            >
              成员
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="classes.length === 0" class="text-center py-12">
      <svg
        class="mx-auto h-12 w-12 text-gray-400"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
        />
      </svg>
      <h3 class="mt-2 text-sm font-medium text-gray-900">暂无组织</h3>
      <p class="mt-1 text-sm text-gray-500">点击上方按钮创建您的第一个组织</p>
    </div>

    <!-- 创建/编辑组织弹窗 -->
    <div
      v-if="showCreateModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 class="text-xl font-bold mb-4">
          {{ editingClass ? '编辑组织' : '创建组织' }}
        </h2>
        <form @submit.prevent="handleSubmit">
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                单位名称 <span class="text-red-500">*</span>
              </label>
              <input
                v-model="form.school_name"
                type="text"
                required
                class="input"
                placeholder="请输入单位名称，如：XX学校"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                级 <span class="text-red-500">*</span>
              </label>
              <input
                v-model="form.session"
                type="text"
                required
                class="input"
                placeholder="请输入级，如：2024"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                班 <span class="text-red-500">*</span>
              </label>
              <input
                v-model="form.class_name"
                type="text"
                required
                class="input"
                placeholder="请输入班，如：高一(1)"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                组织描述
              </label>
              <textarea
                v-model="form.description"
                class="input"
                rows="3"
                placeholder="请输入组织描述（选填）"
              ></textarea>
            </div>
          </div>
          <div class="flex justify-end space-x-3 mt-6">
            <button type="button" @click="closeModal" class="btn-secondary">
              取消
            </button>
            <button type="submit" class="btn-primary">
              {{ editingClass ? '保存' : '创建' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import request from '@/api/request';
import { onActivated, onMounted, ref, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user';
import { getUserAssistantClasses } from '@/api/class';

const router = useRouter();
const route = useRoute();
const userStore = useUserStore();

interface ClassInfo {
  id: number;
  school_name: string;
  session: string;
  class_name: string;
  description?: string;
  status: boolean;
  student_count: number;
}

const classes = ref<ClassInfo[]>([]);
const showCreateModal = ref(false);
const editingClass = ref<ClassInfo | null>(null);
const form = ref({
  school_name: '',
  session: '',
  class_name: '',
  description: '',
});

const isClassAssistant = computed(() => {
  return userStore.userInfo?.role_name === 'class_assistant';
});

const fetchClasses = async () => {
  try {
    if (isClassAssistant.value) {
      // 组织助理获取自己授权的组织列表
      const data = (await getUserAssistantClasses()) as { items: ClassInfo[] };
      classes.value = data.items || [];
    } else {
      // 管理者获取自己的组织列表
      const data = (await request.get('/api/v1/classes/')) as { items: ClassInfo[] };
      classes.value = data.items || [];
    }
  } catch (error) {
    // 获取失败时显示空列表，不跳转页面
    classes.value = [];
    console.log('获取组织列表失败，显示空列表');
  }
};

const handleSubmit = async () => {
  try {
    if (editingClass.value) {
      await request.put(`/api/v1/classes/${editingClass.value.id}`, form.value);
    } else {
      await request.post('/api/v1/classes/', form.value);
    }
    closeModal();
    fetchClasses();
  } catch (error) {
    console.error('保存组织失败:', error);
  }
};

const editClass = (classItem: ClassInfo) => {
  editingClass.value = classItem;
  form.value = {
    school_name: classItem.school_name,
    session: classItem.session,
    class_name: classItem.class_name,
    description: classItem.description || '',
  };
  showCreateModal.value = true;
};

const viewClass = (classItem: ClassInfo) => {
  router.push(`/teacher/classes/${classItem.id}`);
};

const manageStudents = (classItem: ClassInfo) => {
  router.push({
    path: '/teacher/students',
    query: { class_id: classItem.id, class_name: classItem.class_name },
  });
};

const toggleStatus = async (classItem: ClassInfo) => {
  try {
    await request.put(`/api/v1/classes/${classItem.id}/status`, {
      status: !classItem.status,
    });
    classItem.status = !classItem.status;
  } catch (error) {
    console.error('更新组织状态失败:', error);
    alert('更新组织状态失败，请重试');
  }
};

const deleteClass = async (classItem: ClassInfo) => {
  if (classItem.student_count && classItem.student_count > 0) {
    alert('该组织有成员绑定，无法删除');
    return;
  }

  if (confirm('确定要删除这个组织吗？删除后将无法恢复。')) {
    try {
      await request.delete(`/api/v1/classes/${classItem.id}`);
      await fetchClasses();
    } catch (error) {
      console.error('删除组织失败:', error);
      alert('删除组织失败，请重试');
    }
  }
};

const closeModal = () => {
  showCreateModal.value = false;
  editingClass.value = null;
  form.value = {
    school_name: '',
    session: '',
    class_name: '',
    description: '',
  };
};

onMounted(async () => {
  await fetchClasses();

  // 检查是否有 edit 参数，如果有则打开编辑弹窗
  const editId = route.query.edit;
  if (editId) {
    const classToEdit = classes.value.find((c) => c.id === Number(editId));
    if (classToEdit) {
      editClass(classToEdit);
    }
    // 清除 URL 中的 edit 参数
    router.replace({ query: {} });
  }

  // 检查是否有 create 参数，如果有则打开创建弹窗
  const createParam = route.query.create;
  if (createParam === 'true') {
    showCreateModal.value = true;
    // 清除 URL 中的 create 参数
    router.replace({ query: {} });
  }
});

onActivated(async () => {
  await fetchClasses();
});
</script>
