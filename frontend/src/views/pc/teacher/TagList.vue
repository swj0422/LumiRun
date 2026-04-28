<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-900">标签管理</h1>
      <div class="flex space-x-2">
        <button @click="openAddModal" class="btn-primary">添加标签</button>
      </div>
    </div>

    <!-- 学员标签 -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <div class="px-6 py-4 bg-gray-50 border-b border-gray-200">
        <h2 class="text-lg font-medium text-gray-900">学员标签</h2>
      </div>
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th
              class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              标签名称
            </th>
            <th
              class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              标签描述
            </th>
            <th
              class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              创建时间
            </th>
            <th
              class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              操作
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="tag in studentTags" :key="tag.id">
            <td
              class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-center"
            >
              {{ tag.name }}
            </td>
            <td class="px-6 py-4 text-sm text-gray-500 text-center">
              {{ tag.description || '-' }}
            </td>
            <td
              class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 text-center"
            >
              {{ formatDate(tag.created_at) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-center">
              <button
                @click="editTag(tag)"
                class="text-primary-600 hover:text-primary-700 mr-3"
              >
                编辑
              </button>
              <button
                @click="deleteTag(tag)"
                class="text-primary-600 hover:text-primary-700"
              >
                删除
              </button>
            </td>
          </tr>
          <tr v-if="studentTags.length === 0">
            <td
              colspan="4"
              class="px-6 py-12 text-center text-sm text-gray-500"
            >
              暂无学员标签数据
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 成长值标签 -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <div class="px-6 py-4 bg-gray-50 border-b border-gray-200">
        <h2 class="text-lg font-medium text-gray-900">成长值标签</h2>
      </div>
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th
              class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              标签名称
            </th>
            <th
              class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              成长值
            </th>
            <th
              class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              创建时间
            </th>
            <th
              class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              操作
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="tag in growthTags" :key="tag.id">
            <td
              class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-center"
            >
              {{ tag.name }}
            </td>
            <td class="px-6 py-4 text-sm text-gray-500 text-center">
              {{ tag.description || 0 }}
            </td>
            <td
              class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 text-center"
            >
              {{ formatDate(tag.created_at) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-center">
              <button
                @click="editTag(tag)"
                class="text-primary-600 hover:text-primary-700 mr-3"
              >
                编辑
              </button>
              <button
                @click="deleteTag(tag)"
                class="text-primary-600 hover:text-primary-700"
              >
                删除
              </button>
            </td>
          </tr>
          <tr v-if="growthTags.length === 0">
            <td
              colspan="4"
              class="px-6 py-12 text-center text-sm text-gray-500"
            >
              暂无成长值标签数据
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 奖励标签 -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <div class="px-6 py-4 bg-gray-50 border-b border-gray-200">
        <h2 class="text-lg font-medium text-gray-900">奖励标签</h2>
      </div>
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th
              class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              标签名称
            </th>
            <th
              class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              标签描述
            </th>
            <th
              class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              创建时间
            </th>
            <th
              class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              操作
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="tag in giftTags" :key="tag.id">
            <td
              class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-center"
            >
              {{ tag.name }}
            </td>
            <td class="px-6 py-4 text-sm text-gray-500 text-center">
              {{ tag.description || '-' }}
            </td>
            <td
              class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 text-center"
            >
              {{ formatDate(tag.created_at) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-center">
              <button
                @click="editTag(tag)"
                class="text-primary-600 hover:text-primary-700 mr-3"
              >
                编辑
              </button>
              <button
                @click="deleteTag(tag)"
                class="text-primary-600 hover:text-primary-700"
              >
                删除
              </button>
            </td>
          </tr>
          <tr v-if="giftTags.length === 0">
            <td
              colspan="4"
              class="px-6 py-12 text-center text-sm text-gray-500"
            >
              暂无奖励标签数据
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 添加/编辑标签弹窗 -->
    <div
      v-if="showAddModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg p-6 w-full max-w-lg">
        <h2 class="text-xl font-bold mb-4">
          {{ editingTag ? '编辑标签' : '添加标签' }}
        </h2>
        <form @submit.prevent="handleSubmit">
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1"
                >标签名称 <span class="text-red-500">*</span></label
              >
              <input
                v-model="form.name"
                type="text"
                required
                class="input"
                placeholder="请输入标签名称"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1"
                >标签类型 <span class="text-red-500">*</span></label
              >
              <select v-model="form.type" required class="input">
                <option value="">请选择标签类型</option>
                <option value="student">学员标签</option>
                <option value="growth">成长值标签</option>
                <option value="gift">奖励标签</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">{{
                form.type === 'growth' ? '成长值' : '标签描述'
              }}</label>
              <input
                v-if="form.type === 'growth'"
                v-model.number="form.description"
                type="number"
                class="input"
                placeholder="请输入成长值"
              />
              <textarea
                v-else
                v-model="form.description"
                class="input h-24 resize-none"
                placeholder="请输入标签描述"
              ></textarea>
            </div>
          </div>
          <div class="flex justify-end space-x-3 mt-6">
            <button type="button" @click="closeAddModal" class="btn-secondary">
              取消
            </button>
            <button type="submit" class="btn-primary">
              {{ editingTag ? '保存' : '添加' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import request from '@/api/request';
import { useUserStore } from '@/stores/user';
import { computed, onMounted, ref } from 'vue';

interface Tag {
  id: number;
  name: string;
  type: string;
  description: string;
  created_at: string;
  updated_at: string;
}

const tags = ref<Tag[]>([]);
const showAddModal = ref(false);
const editingTag = ref<Tag | null>(null);
const form = ref({
  name: '',
  type: '',
  description: '',
});

const userStore = useUserStore();

// 按类型过滤标签
const studentTags = computed(() => {
  return tags.value.filter((tag) => tag.type === 'student');
});

const growthTags = computed(() => {
  return tags.value.filter((tag) => tag.type === 'growth');
});

const giftTags = computed(() => {
  return tags.value.filter((tag) => tag.type === 'gift');
});

// const getTagTypeText = (type: string): string => {
//   switch (type) {
//     case 'student':
//       return '学员标签'
//     case 'growth':
//       return '成长值标签'
//     case 'gift':
//       return '奖励标签'
//     default:
//       return type
//   }
// }

const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
};

const fetchTags = async () => {
  try {
    // 添加时间戳参数，防止浏览器缓存
    const timestamp = new Date().getTime();
    const data = await request.get(`/api/v1/tags/?t=${timestamp}`);
    tags.value = data?.items || [];
  } catch (error) {
    console.error('获取标签列表失败:', error);
    tags.value = [];
  }
};

const openAddModal = () => {
  editingTag.value = null;
  form.value = { name: '', type: '', description: '' };
  showAddModal.value = true;
};

const closeAddModal = () => {
  showAddModal.value = false;
  editingTag.value = null;
};

const editTag = (tag: Tag) => {
  editingTag.value = tag;
  form.value = {
    name: tag.name,
    type: tag.type,
    description: tag.description,
  };
  showAddModal.value = true;
};

const handleSubmit = async () => {
  if (!form.value.name) {
    alert('请输入标签名称');
    return;
  }
  if (!form.value.type) {
    alert('请选择标签类型');
    return;
  }
  try {
    // 确保description字段是字符串类型
    const submitData = {
      ...form.value,
      description:
        form.value.description !== undefined && form.value.description !== null
          ? String(form.value.description)
          : '',
    };
    if (editingTag.value) {
      // 编辑标签，只更新当前行
      await request.put(`/api/v1/tags/${editingTag.value.id}`, submitData);

      // 更新本地数据
      const index = tags.value.findIndex(
        (tag) => tag.id === editingTag.value?.id
      );
      if (index !== -1) {
        tags.value[index] = {
          ...tags.value[index],
          name: form.value.name,
          type: form.value.type,
          description: submitData.description,
          updated_at: new Date().toISOString(),
        };
      }
    } else {
      // 添加新标签，刷新整个列表
      const response = await request.post('/api/v1/tags/', submitData);
      // 将新标签添加到列表中
      tags.value.push(response);
    }
    closeAddModal();
  } catch (error: any) {
    console.error('保存标签失败:', error);
    const errorMessage =
      error?.response?.data?.detail || error?.message || '保存失败，请重试';
    alert(errorMessage);
  }
};

const deleteTag = async (tag: Tag) => {
  if (confirm(`确定要删除标签 "${tag.name}" 吗？`)) {
    try {
      await request.delete(`/api/v1/tags/${tag.id}`);

      // 从本地数据中移除标签
      const index = tags.value.findIndex((t) => t.id === tag.id);
      if (index !== -1) {
        tags.value.splice(index, 1);
      }

      alert('删除成功');
    } catch (error) {
      console.error('删除标签失败:', error);
      alert('删除失败，请重试');
    }
  }
};

onMounted(async () => {
  // 检查用户是否已登录
  if (!userStore.isLoggedIn && userStore.token) {
    try {
      await userStore.fetchUserInfo();
    } catch (error) {
      console.error('获取用户信息失败:', error);
    }
  }

  // 只有在用户已登录的情况下才调用API
  if (userStore.isLoggedIn) {
    fetchTags();
  }
});
</script>
