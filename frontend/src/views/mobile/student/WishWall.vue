<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 顶部导航 -->
    <div class="bg-white shadow-sm">
      <div class="max-w-md mx-auto px-4 py-3 flex items-center justify-between">
        <button @click="goBack" class="w-8 h-8 flex items-center justify-center">
          <svg class="w-6 h-6 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <h1 class="text-lg font-semibold text-gray-800">心愿墙</h1>
        <button @click="showCreateModal = true" class="w-8 h-8 flex items-center justify-center">
          <svg class="w-6 h-6 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
        </button>
      </div>
    </div>

    <!-- 我的心愿列表 -->
    <div class="px-4 py-4">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">我的心愿</h2>
      
      <div v-if="myWishes.length > 0" class="space-y-3">
        <div
          v-for="wish in myWishes"
          :key="wish.id"
          class="card p-4"
        >
          <div class="flex justify-between items-start mb-3">
            <h3 class="font-medium text-gray-800">{{ wish.title }}</h3>
            <span 
              :class="{
                'px-2 py-0.5 rounded-full text-xs': true,
                'bg-primary-100 text-primary-800': wish.status === 0,
                'bg-success-100 text-success-800': wish.status === 1,
                'bg-gray-100 text-gray-800': wish.status === 2
              }"
            >
              {{ ["待处理", "已实现", "已拒绝"][wish.status] }}
            </span>
          </div>
          
          <p v-if="wish.description" class="text-sm text-gray-500 mb-3">{{ wish.description }}</p>
          
          <div v-if="wish.image_urls && wish.image_urls.length > 0" class="flex space-x-2 mb-3">
            <img
              v-for="(img, idx) in wish.image_urls"
              :key="idx"
              :src="img"
              class="w-20 h-20 rounded-lg object-cover"
            />
          </div>
          
          <div v-if="wish.teacher_comment" class="bg-primary-50 p-3 rounded-lg">
            <p class="text-xs text-primary-600 mb-1">导师回复</p>
            <p class="text-sm text-primary-800">{{ wish.teacher_comment }}</p>
          </div>
          
          <div class="flex items-center justify-between mt-3">
            <span class="text-xs text-gray-400">{{ formatDate(wish.created_at) }}</span>
            <div v-if="wish.status === 0" class="flex space-x-2">
              <button @click="editWish(wish)" class="text-xs text-primary-600">编辑</button>
              <button @click="deleteWish(wish.id)" class="text-xs text-danger-600">删除</button>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="card p-8 text-center">
        <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg class="w-8 h-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        </div>
        <p class="text-gray-500">暂无心愿</p>
        <p class="text-sm text-gray-400 mt-1">点击右上角按钮创建心愿</p>
      </div>
    </div>

    <!-- 创建/编辑心愿弹窗 -->
    <div
      v-if="showCreateModal"
      class="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50"
    >
      <div class="relative w-full max-w-md mx-4">
        <div class="bg-white rounded-lg p-4 max-h-[80vh] overflow-y-auto">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-semibold text-gray-900">{{ editingWish ? '编辑心愿' : '创建心愿' }}</h3>
            <button
              @click="closeModal"
              class="text-gray-500 hover:text-gray-700"
            >
              <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">心愿标题 *</label>
              <input
                v-model="formData.title"
                type="text"
                placeholder="请输入心愿标题"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">心愿描述</label>
              <textarea
                v-model="formData.description"
                placeholder="请描述你的心愿（可选）"
                rows="3"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              ></textarea>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">选择班级 *</label>
              <select
                v-model="formData.class_id"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="">请选择班级</option>
                <option v-for="cls in bindClasses" :key="cls.id" :value="cls.id">
                  {{ cls.school_name }} {{ cls.session }}级 {{ cls.class_name }}班
                </option>
              </select>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">上传图片（最多3张）</label>
              <div class="flex space-x-2">
                <div
                  v-for="(img, idx) in formData.images"
                  :key="idx"
                  class="relative w-20 h-20 rounded-lg overflow-hidden"
                >
                  <img :src="img" class="w-full h-full object-cover" />
                  <button
                    @click="removeImage(idx)"
                    class="absolute top-1 right-1 w-6 h-6 bg-black bg-opacity-50 rounded-full flex items-center justify-center"
                  >
                    <svg class="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
                <div
                  v-if="formData.images.length < 3"
                  @click="triggerFileInput"
                  class="w-20 h-20 rounded-lg border-2 border-dashed border-gray-300 flex items-center justify-center cursor-pointer hover:border-primary-500"
                >
                  <svg class="w-6 h-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
              </div>
              <p class="text-xs text-gray-400 mt-1">支持 JPG、PNG 格式，最多上传3张</p>
              <input
                ref="fileInput"
                type="file"
                multiple
                accept="image/*"
                class="hidden"
                @change="handleFileSelect"
              />
            </div>
          </div>
          
          <button
            @click="submitWish"
            class="w-full btn-primary mt-6 py-2"
            :disabled="!formData.title || !formData.class_id"
          >
            {{ editingWish ? '保存修改' : '创建心愿' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import request from '@/api/request';
import { ref, onMounted } from 'vue';

const myWishes = ref<any[]>([]);
const bindClasses = ref<any[]>([]);
const showCreateModal = ref(false);
const editingWish = ref<any>(null);
const fileInput = ref<HTMLInputElement | null>(null);

const formData = ref({
  title: '',
  description: '',
  class_id: '',
  images: [] as string[]
});

const goBack = () => {
  window.history.back();
};

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString('zh-CN');
};

const fetchMyWishes = async () => {
  try {
    const response = await request.get('/api/v1/wishes/my');
    if (response && response.items) {
      myWishes.value = response.items;
    }
  } catch (error) {
    console.error('获取心愿列表失败:', error);
  }
};

const fetchBindClasses = async () => {
  try {
    const response = await request.get('/api/v1/students/my-classes');
    if (response) {
      bindClasses.value = response.filter((c: any) => c.bind_status === 'approved');
    }
  } catch (error) {
    console.error('获取绑定班级失败:', error);
  }
};

const triggerFileInput = () => {
  fileInput.value?.click();
};

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement;
  const files = target.files;
  if (files) {
    const maxCount = 3 - formData.value.images.length;
    for (let i = 0; i < Math.min(files.length, maxCount); i++) {
      const file = files[i];
      const reader = new FileReader();
      reader.onload = (e) => {
        formData.value.images.push(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  }
  target.value = '';
};

const removeImage = (index: number) => {
  formData.value.images.splice(index, 1);
};

const closeModal = () => {
  showCreateModal.value = false;
  editingWish.value = null;
  formData.value = {
    title: '',
    description: '',
    class_id: '',
    images: []
  };
};

const editWish = (wish: any) => {
  editingWish.value = wish;
  formData.value = {
    title: wish.title,
    description: wish.description || '',
    class_id: wish.class_id.toString(),
    images: wish.image_urls || []
  };
  showCreateModal.value = true;
};

const submitWish = async () => {
  if (!formData.value.title || !formData.value.class_id) {
    alert('请填写必填项');
    return;
  }

  try {
    const form = new FormData();
    form.append('title', formData.value.title);
    if (formData.value.description) {
      form.append('description', formData.value.description);
    }
    form.append('class_id', formData.value.class_id);

    // 上传图片（仅新增的Base64图片）
    for (let i = 0; i < formData.value.images.length; i++) {
      const img = formData.value.images[i];
      if (img.startsWith('data:')) {
        const blob = await fetch(img).then(res => res.blob());
        form.append('images', blob, `wish_${Date.now()}_${i}.jpg`);
      }
    }

    if (editingWish.value) {
      await request.put(`/api/v1/wishes/${editingWish.value.id}`, {
        title: formData.value.title,
        description: formData.value.description
      });
    } else {
      await request.post('/api/v1/wishes/', form, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
    }

    closeModal();
    await fetchMyWishes();
  } catch (error) {
    console.error('提交心愿失败:', error);
    alert('提交失败，请稍后重试');
  }
};

const deleteWish = async (wishId: number) => {
  if (!confirm('确定要删除这个心愿吗？')) {
    return;
  }

  try {
    await request.delete(`/api/v1/wishes/${wishId}`);
    await fetchMyWishes();
  } catch (error) {
    console.error('删除心愿失败:', error);
    alert('删除失败，请稍后重试');
  }
};

onMounted(async () => {
  await fetchMyWishes();
  await fetchBindClasses();
});
</script>