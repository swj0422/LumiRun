<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-900">奖励管理</h1>
      <button @click="showCreateModal = true" class="btn-primary">
        添加奖励
      </button>
    </div>

    <!-- 奖励列表 -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <div
        v-for="gift in gifts"
        :key="gift.id"
        class="bg-white rounded-lg shadow overflow-hidden"
      >
        <div class="aspect-w-16 aspect-h-9 bg-gray-200">
          <img
            v-if="gift.image_path"
            :src="gift.image_path"
            :alt="gift.name"
            class="w-full h-48 object-cover"
          />
          <div
            v-else
            class="w-full h-48 flex items-center justify-center text-gray-400"
          >
            <svg
              class="w-12 h-12"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 6v6m0 0v6m0-6h6m-6 0H6"
              />
            </svg>
          </div>
        </div>
        <div class="p-4">
          <h3 class="text-lg font-semibold text-gray-900 mb-2">
            {{ gift.name }}
          </h3>
          <p class="text-sm text-gray-500 mb-2">
            {{ gift.description || '暂无描述' }}
          </p>
          <div class="flex justify-between items-center">
            <span class="text-blue-600 font-bold">{{ gift.price }} 积分</span>
            <span class="text-sm text-gray-500">库存: {{ gift.stock }}</span>
          </div>
          <div class="flex justify-between items-center mt-3">
            <span
              :class="
                gift.status
                  ? 'bg-green-100 text-green-800'
                  : 'bg-gray-100 text-gray-800'
              "
              class="px-2 py-1 text-xs rounded-full"
            >
              {{ gift.status ? '上架' : '下架' }}
            </span>
            <div class="space-x-2">
              <button
                @click="editGift(gift)"
                class="text-primary-600 hover:text-primary-700"
              >
                编辑
              </button>
              <button
                @click="toggleStatus(gift)"
                class="text-primary-600 hover:text-primary-700"
              >
                {{ gift.status ? '下架' : '上架' }}
              </button>
              <button
                @click="manageClasses(gift)"
                class="text-primary-600 hover:text-primary-700"
              >
                组织设置
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="gifts.length === 0" class="text-center py-12">
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
          d="M12 6v6m0 0v6m0-6h6m-6 0H6"
        />
      </svg>
      <h3 class="mt-2 text-sm font-medium text-gray-900">暂无奖励</h3>
      <p class="mt-1 text-sm text-gray-500">点击上方按钮添加您的第一个奖励</p>
    </div>

    <!-- 创建/编辑奖励弹窗 -->
    <div
      v-if="showCreateModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 class="text-xl font-bold mb-4">
          {{ editingGift ? '编辑奖励' : '添加奖励' }}
        </h2>
        <form @submit.prevent="handleSubmit">
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                奖励名称 <span class="text-red-500">*</span>
              </label>
              <input
                v-model="form.name"
                type="text"
                required
                class="input"
                placeholder="请输入奖励名称"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                描述
              </label>
              <textarea
                v-model="form.description"
                class="input"
                rows="2"
                placeholder="请输入奖励描述（选填）"
              ></textarea>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  所需积分/份 <span class="text-red-500">*</span>
                </label>
                <input
                  v-model.number="form.price"
                  type="number"
                  required
                  min="1"
                  class="input"
                  placeholder="积分"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  库存 <span class="text-red-500">*</span>
                </label>
                <input
                  v-model.number="form.stock"
                  type="number"
                  required
                  min="0"
                  class="input"
                  placeholder="库存数量"
                />
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                奖励图片 <span class="text-red-500">*</span>
                <span class="text-xs text-gray-500 ml-2">
                  (最多9张，最少1张)
                </span>
              </label>
              <div class="flex flex-wrap gap-2">
                <div
                  v-for="(image, index) in form.images"
                  :key="index"
                  class="relative w-20 h-20 bg-gray-100 rounded-md overflow-hidden"
                >
                  <img
                    :src="typeof image === 'string' ? image : image.url"
                    :alt="`奖励图片 ${index + 1}`"
                    class="w-full h-full object-cover"
                  />
                  <button
                    type="button"
                    @click="removeImage(index)"
                    class="absolute top-1 right-1 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center"
                  >
                    ×
                  </button>
                </div>
                <div
                  v-if="form.images.length < 9"
                  class="w-20 h-20 border-2 border-dashed border-gray-300 rounded-md flex items-center justify-center cursor-pointer"
                  @click="triggerFileInput"
                >
                  <input
                    ref="fileInput"
                    type="file"
                    multiple
                    accept="image/*"
                    class="hidden"
                    @change="handleImageUpload"
                  />
                  <svg
                    class="w-8 h-8 text-gray-400"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                    />
                  </svg>
                </div>
              </div>
              <p
                v-if="form.images.length === 0"
                class="text-xs text-red-500 mt-1"
              >
                请至少上传1张图片
              </p>
              <p
                v-else-if="form.images.length > 9"
                class="text-xs text-red-500 mt-1"
              >
                最多只能上传9张图片
              </p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                适用组织
              </label>
              <div class="space-y-2">
                <div class="flex items-center">
                  <input
                    type="checkbox"
                    v-model="form.selectAllClasses"
                    @change="toggleSelectAllClasses"
                    class="mr-2"
                  />
                  <label class="text-sm text-gray-700"> 全部未关闭组织 </label>
                </div>
                <div
                  v-for="cls in classes"
                  :key="cls.id"
                  class="flex items-center ml-6"
                >
                  <input
                    type="checkbox"
                    v-model="form.selectedClasses"
                    :value="cls.id"
                    @change="updateSelectAll"
                    class="mr-2"
                  />
                  <label class="text-sm text-gray-700">
                    {{ cls.school_name }} - {{ cls.session }} -
                    {{ cls.class_name }}
                  </label>
                </div>
              </div>
            </div>
          </div>
          <div class="flex justify-end space-x-3 mt-6">
            <button type="button" @click="closeModal" class="btn-secondary">
              取消
            </button>
            <button
              type="submit"
              :disabled="form.images.length === 0 || form.images.length > 9"
              class="btn-primary"
            >
              {{ editingGift ? '保存' : '创建' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 组织设置弹窗 -->
    <div
      v-if="showClassModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 class="text-xl font-bold mb-4">设置奖励适用组织</h2>
        <div class="space-y-4">
          <div class="flex items-center">
            <input
              type="checkbox"
              v-model="classForm.selectAllClasses"
              @change="toggleSelectAllClassForm"
              class="mr-2"
            />
            <label class="text-sm text-gray-700"> 全部未关闭组织 </label>
          </div>
          <div
            v-for="cls in classes"
            :key="cls.id"
            class="flex items-center ml-6"
          >
            <input
              type="checkbox"
              v-model="classForm.selectedClasses"
              :value="cls.id"
              @change="updateSelectAllClassForm"
              class="mr-2"
            />
            <label class="text-sm text-gray-700">
              {{ cls.school_name }} - {{ cls.session }} - {{ cls.class_name }}
            </label>
          </div>
        </div>
        <div class="flex justify-end space-x-3 mt-6">
          <button type="button" @click="closeClassModal" class="btn-secondary">
            取消
          </button>
          <button type="button" @click="saveClassSettings" class="btn-primary">
            保存
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import request from '@/api/request';
import { onActivated, onMounted, ref } from 'vue';

interface Gift {
  id: number;
  name: string;
  description?: string;
  price: number;
  stock: number;
  status: boolean;
  image_path?: string;
  images?: Array<{ url: string } | string>;
}

interface ClassInfo {
  id: number;
  class_name: string;
  school_name?: string;
  session?: string;
}

const gifts = ref<Gift[]>([]);
const classes = ref<ClassInfo[]>([]);
const showCreateModal = ref(false);
const showClassModal = ref(false);
const editingGift = ref<Gift | null>(null);
const currentGift = ref<Gift | null>(null);
const fileInput = ref<HTMLInputElement | null>(null);
const form = ref({
  name: '',
  description: '',
  price: 1,
  stock: 0,
  status: true,
  images: [] as Array<{ url: string } | string>,
  selectedClasses: [] as number[],
  selectAllClasses: true,
});

const classForm = ref({
  selectedClasses: [] as number[],
  selectAllClasses: true,
});

const fetchGifts = async () => {
  try {
    console.log('开始获取奖励列表');
    console.log('当前token:', localStorage.getItem('token'));
    const data = (await request.get('/api/v1/gifts/')) as { items: Gift[] };
    console.log('获取奖励列表成功:', data);
    gifts.value = data.items || [];
  } catch (error) {
    // 获取失败时显示空列表，不跳转页面
    gifts.value = [];
    console.error('获取奖励列表失败:', error);
  }
};

const fetchClasses = async () => {
  try {
    const data = (await request.get('/api/v1/classes/')) as
      | { items: ClassInfo[] }
      | ClassInfo[];
    if (Array.isArray(data)) {
      classes.value = data;
    } else if (data && data.items) {
      classes.value = data.items;
    } else {
      classes.value = [];
    }
  } catch (error) {
    classes.value = [];
    console.log('获取组织列表失败，显示空列表');
  }
};

const triggerFileInput = () => {
  fileInput.value?.click();
};

const handleImageUpload = (event: Event) => {
  const target = event.target as HTMLInputElement;
  const files = target.files;
  if (!files) return;

  const remainingSlots = 9 - form.value.images.length;
  const filesToAdd = Math.min(files.length, remainingSlots);

  for (let i = 0; i < filesToAdd; i++) {
    const file = files[i];
    const reader = new FileReader();
    reader.onload = (e) => {
      const result = e.target?.result as string;
      form.value.images.push(result);
    };
    reader.readAsDataURL(file);
  }

  // 清空文件输入，以便可以重复选择相同的文件
  target.value = '';
};

const removeImage = (index: number) => {
  form.value.images.splice(index, 1);
};

const handleSubmit = async () => {
  try {
    // 检查必填项目
    if (!form.value.name) {
      alert('请输入奖励名称');
      return;
    }
    if (!form.value.price || form.value.price < 0) {
      alert('请输入有效的价格');
      return;
    }
    if (!form.value.stock || form.value.stock < 0) {
      alert('请输入有效的库存');
      return;
    }
    if (form.value.images.length === 0) {
      alert('请至少上传1张图片');
      return;
    }

    // 构建表单数据
    const formData = new FormData();
    formData.append('name', form.value.name);
    formData.append('description', form.value.description || '');
    formData.append('price', form.value.price.toString());
    formData.append('stock', form.value.stock.toString());
    formData.append('status', form.value.status ? '1' : '0');

    // 处理图片上传
    form.value.images.forEach((image, index) => {
      console.log(
        '[DEBUG] Processing image:',
        image,
        'index:',
        index,
        'type:',
        typeof image
      );
      if (typeof image === 'string' && image.startsWith('data:')) {
        // 从 data URL 创建 Blob
        console.log('[DEBUG] Image is data URL, converting to blob');
        const blob = dataURLToBlob(image);
        formData.append(`images`, blob, `image_${index}.jpg`);
        console.log('[DEBUG] Added blob to formData');
      } else if (typeof image === 'string') {
        // 已存在的图片 URL，直接添加
        console.log('[DEBUG] Image is URL, skipping upload');
        // 不需要重新上传已存在的图片
      } else if (
        typeof image === 'object' &&
        image !== null &&
        'url' in image
      ) {
        // 对象类型的图片 { url: string }
        console.log('[DEBUG] Image is object with url:', image.url);
        // 不需要重新上传已存在的图片
      } else if (typeof image === 'object' && image !== null) {
        // 类型断言为 any，解决 instanceof 类型检查问题
        if ((image as any) instanceof Blob) {
          // Blob 对象，直接添加
          console.log('[DEBUG] Image is Blob, adding to formData');
          formData.append(`images`, image, `image_${index}.jpg`);
          console.log('[DEBUG] Added blob to formData');
        }
      } else {
        console.log('[DEBUG] Unknown image type:', typeof image, image);
      }
    });

    const uploadedImages = formData.getAll('images');
    console.log('[DEBUG] FormData entries count:', uploadedImages.length);

    // 如果没有上传新图片，使用 JSON 格式更新
    if (uploadedImages.length === 0) {
      console.log('[DEBUG] No new images uploaded, using JSON format');
      const jsonData = {
        name: form.value.name,
        description: form.value.description || '',
        price: form.value.price,
        stock: form.value.stock,
        status: form.value.status ? 1 : 0,
      };

      if (editingGift.value) {
        await request.put(`/api/v1/gifts/${editingGift.value.id}/`, jsonData);
      } else {
        const response = await request.post('/api/v1/gifts/', jsonData);
        if (response.id) {
          await updateGiftClasses(response.id, form.value.selectedClasses);
        }
      }
    } else {
      // 有新图片上传，使用 FormData 格式
      console.log('[DEBUG] New images uploaded, using FormData format');
      if (editingGift.value) {
        await request.put(`/api/v1/gifts/${editingGift.value.id}/`, formData);
        await updateGiftClasses(
          editingGift.value.id,
          form.value.selectedClasses
        );
      } else {
        const response = await request.post('/api/v1/gifts/', formData);
        if (response.id) {
          await updateGiftClasses(response.id, form.value.selectedClasses);
        }
      }
    }
    closeModal();
    fetchGifts();
  } catch (error) {
    console.error('保存奖励失败:', error);
  }
};

const updateGiftClasses = async (giftId: number, classIds: number[]) => {
  try {
    // 先获取当前奖励的组织列表
    const currentClasses = (await request.get(
      `/api/v1/gifts/${giftId}/classes`
    )) as { classes: Array<{ class_id: number }> };
    const currentClassIds = currentClasses.classes.map((c) => c.class_id);

    // 移除不再选择的组织
    for (const classId of currentClassIds) {
      if (!classIds.includes(classId)) {
        await request.delete(`/api/v1/gifts/class/${giftId}/${classId}`);
      }
    }

    // 添加新选择的组织
    for (const classId of classIds) {
      if (!currentClassIds.includes(classId)) {
        await request.post('/api/v1/gifts/class', {
          gift_id: giftId,
          class_id: classId,
        });
      }
    }
  } catch (error) {
    console.error('更新奖励组织失败:', error);
  }
};

const dataURLToBlob = (dataURL: string) => {
  const arr = dataURL.split(',');
  const mime = arr[0].match(/:(.*?);/)?.[1] || 'image/jpeg';
  const bstr = atob(arr[1]);
  let n = bstr.length;
  const u8arr = new Uint8Array(n);
  while (n--) {
    u8arr[n] = bstr.charCodeAt(n);
  }
  return new Blob([u8arr], { type: mime });
};

const editGift = async (gift: Gift) => {
  editingGift.value = gift;
  form.value = {
    name: gift.name,
    description: gift.description || '',
    price: gift.price,
    stock: gift.stock,
    status: gift.status,
    images: gift.images || (gift.image_path ? [gift.image_path] : []),
    selectedClasses: [],
    selectAllClasses: true,
  };

  // 获取当前奖励的组织列表
  try {
    const response = (await request.get(`/api/v1/gifts/${gift.id}/classes`)) as {
      classes: Array<{ class_id: number }>;
    };
    form.value.selectedClasses = response.classes.map((c) => c.class_id);
    form.value.selectAllClasses =
      form.value.selectedClasses.length === classes.value.length;
  } catch (error) {
    console.error('获取奖励组织失败:', error);
  }

  showCreateModal.value = true;
};

const toggleStatus = async (gift: Gift) => {
  try {
    await request.put(`/api/v1/gifts/${gift.id}/`, {
      status: gift.status ? 0 : 1,
    });
    gift.status = !gift.status;
  } catch (error) {
    console.error('更新奖励状态失败:', error);
    alert('更新奖励状态失败，请重试');
  }
};

const manageClasses = async (gift: Gift) => {
  currentGift.value = gift;
  classForm.value = {
    selectedClasses: [],
    selectAllClasses: true,
  };

  // 获取当前奖励的组织列表
  try {
    const response = (await request.get(`/api/v1/gifts/${gift.id}/classes`)) as {
      classes: Array<{ class_id: number }>;
    };
    classForm.value.selectedClasses = response.classes.map((c) => c.class_id);
    classForm.value.selectAllClasses =
      classForm.value.selectedClasses.length === classes.value.length;
  } catch (error) {
    console.error('获取奖励组织失败:', error);
  }

  showClassModal.value = true;
};

const saveClassSettings = async () => {
  if (!currentGift.value) return;

  try {
    await updateGiftClasses(
      currentGift.value.id,
      classForm.value.selectedClasses
    );
    closeClassModal();
  } catch (error) {
    console.error('保存组织设置失败:', error);
  }
};

const closeClassModal = () => {
  showClassModal.value = false;
  currentGift.value = null;
  classForm.value = { selectedClasses: [], selectAllClasses: true };
};

const closeModal = () => {
  showCreateModal.value = false;
  editingGift.value = null;
  form.value = {
    name: '',
    description: '',
    price: 1,
    stock: 0,
    status: true,
    images: [],
    selectedClasses: [],
    selectAllClasses: true,
  };
};

const toggleSelectAllClasses = () => {
  if (form.value.selectAllClasses) {
    form.value.selectedClasses = classes.value.map((c) => c.id);
  } else {
    form.value.selectedClasses = [];
  }
};

const updateSelectAll = () => {
  form.value.selectAllClasses =
    form.value.selectedClasses.length === classes.value.length;
};

const toggleSelectAllClassForm = () => {
  if (classForm.value.selectAllClasses) {
    classForm.value.selectedClasses = classes.value.map((c) => c.id);
  } else {
    classForm.value.selectedClasses = [];
  }
};

const updateSelectAllClassForm = () => {
  classForm.value.selectAllClasses =
    classForm.value.selectedClasses.length === classes.value.length;
};

onMounted(async () => {
  await fetchClasses();
  await fetchGifts();
});

onActivated(async () => {
  await fetchClasses();
  await fetchGifts();
});
</script>
