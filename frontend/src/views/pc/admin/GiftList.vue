<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-900">礼品管理</h1>
      <div class="text-sm text-gray-500">
        管理员不能创建礼品，仅可管理现有礼品
      </div>
    </div>

    <div class="bg-white rounded-lg shadow p-4">
      <div class="flex flex-wrap gap-4">
        <input
          v-model="searchKeyword"
          type="text"
          class="input flex-1 min-w-[200px]"
          placeholder="搜索礼品名称"
          @input="handleSearch"
        />
        <select v-model="selectedTeacher" class="input w-48" @change="fetchGifts">
          <option value="">全部管理者</option>
          <option v-for="teacher in teachers" :key="teacher.id" :value="teacher.id">{{ teacher.real_name }}</option>
        </select>
        <select v-model="selectedClass" class="input w-48" @change="fetchGifts">
          <option value="">全部组织</option>
          <option v-for="cls in classes" :key="cls.id" :value="cls.id">{{ cls.class_name }}</option>
        </select>
        <select v-model="selectedStatus" class="input w-32" @change="fetchGifts">
          <option value="">全部状态</option>
          <option value="true">上架</option>
          <option value="false">下架</option>
        </select>
      </div>
    </div>

    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">礼品</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">所需成长值</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">库存</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">创建管理者</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">创建时间</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="gift in gifts" :key="gift.id">
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="flex items-center">
                <div v-if="gift.image_url" class="w-10 h-10 rounded-lg overflow-hidden mr-3">
                  <img :src="gift.image_url" class="w-full h-full object-cover" />
                </div>
                <div v-else class="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center mr-3">
                  <svg class="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v13m0-13V6a2 2 0 112 2h-2zm0 0V5.5A2.5 2.5 0 109.5 8H12zm-7 4h14M5 12a2 2 0 110-4h14a2 2 0 110 4M5 12v7a2 2 0 002 2h10a2 2 0 002-2v-7" />
                  </svg>
                </div>
                <div>
                  <p class="text-sm font-medium text-gray-900">{{ gift.name }}</p>
                  <p class="text-xs text-gray-500 truncate max-w-[200px]">{{ gift.description || '-' }}</p>
                </div>
              </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-primary-600">{{ gift.price }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ gift.stock?.current_stock || 0 }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ gift.creator_name || '-' }}</td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="gift.status ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'" class="px-2 py-1 text-xs rounded-full">
                {{ gift.status ? '上架' : '下架' }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ formatDate(gift.created_at) }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
              <button
                v-if="gift.status"
                @click="offlineGift(gift.id)"
                class="text-yellow-600 hover:text-yellow-700 mr-2"
              >
                下架
              </button>
              <button v-else @click="onlineGift(gift.id)" class="text-green-600 hover:text-green-700 mr-2">上架</button>
              <button @click="openStockModal(gift)" class="text-blue-600 hover:text-blue-700 mr-2">修改库存</button>
              <button @click="deleteGift(gift)" class="text-red-600 hover:text-red-700">删除</button>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="gifts.length === 0" class="text-center py-12">
        <p class="text-gray-500">暂无礼品数据</p>
      </div>
    </div>

    <div v-if="showStockModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
        <h2 class="text-xl font-bold mb-4">修改库存</h2>
        <div class="space-y-4">
          <div>
            <p class="text-sm text-gray-600 mb-2">礼品: {{ selectedGift?.name }}</p>
            <p class="text-sm text-gray-500 mb-4">当前库存: {{ selectedGift?.stock }}</p>
            <label class="block text-sm font-medium text-gray-700 mb-1">新库存数量</label>
            <input v-model.number="newStock" type="number" min="0" class="input w-full" placeholder="请输入库存数量" />
          </div>
          <div class="flex justify-end gap-2">
            <button @click="showStockModal = false" class="btn-secondary">取消</button>
            <button @click="updateStock" class="btn-primary">保存</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import request from '@/api/request';
import { onMounted, ref } from 'vue';

interface Gift {
  id: number;
  name: string;
  description: string;
  image_url: string;
  required_points: number;
  stock: number;
  creator_id: number;
  creator_name: string;
  status: boolean;
  created_at: string;
}

interface Teacher {
  id: number;
  real_name: string;
}

interface ClassInfo {
  id: number;
  class_name: string;
}

const gifts = ref<Gift[]>([]);
const teachers = ref<Teacher[]>([]);
const classes = ref<ClassInfo[]>([]);
const searchKeyword = ref('');
const selectedTeacher = ref('');
const selectedClass = ref('');
const selectedStatus = ref('');
const showStockModal = ref(false);
const selectedGift = ref<Gift | null>(null);
const newStock = ref(0);

const fetchGifts = async () => {
  try {
    const params: Record<string, any> = {};
    if (selectedTeacher.value) params.teacher_id = selectedTeacher.value;
    if (selectedClass.value) params.class_id = selectedClass.value;
    if (selectedStatus.value) params.status = selectedStatus.value === 'true';
    if (searchKeyword.value) params.keyword = searchKeyword.value;
    const data = (await request.get('/api/v1/admin/gifts', { params })) as { items: Gift[] };
    gifts.value = data.items || [];
  } catch (error) {
    console.error('获取礼品列表失败:', error);
  }
};

const fetchTeachers = async () => {
  try {
    const data = (await request.get('/api/v1/admin/users', { params: { role_id: 3 } })) as { items: Teacher[] };
    teachers.value = data.items || [];
  } catch (error) {
    console.error('获取管理者列表失败:', error);
  }
};

const fetchClasses = async () => {
  try {
    const data = (await request.get('/api/v1/admin/classes')) as { items: ClassInfo[] };
    classes.value = data.items || [];
  } catch (error) {
    console.error('获取组织列表失败:', error);
  }
};

const handleSearch = () => {
  fetchGifts();
};

const onlineGift = async (giftId: number) => {
  try {
    await request.put(`/api/v1/admin/gifts/${giftId}/status`, { status: true });
    fetchGifts();
  } catch (error) {
    console.error('上架礼品失败:', error);
  }
};

const offlineGift = async (giftId: number) => {
  if (!confirm('确定要下架该礼品吗？')) return;
  try {
    await request.put(`/api/v1/admin/gifts/${giftId}/status`, { status: false });
    fetchGifts();
  } catch (error) {
    console.error('下架礼品失败:', error);
  }
};

const openStockModal = (gift: Gift) => {
  selectedGift.value = gift;
  newStock.value = gift.stock;
  showStockModal.value = true;
};

const updateStock = async () => {
  if (!selectedGift.value) return;
  try {
    await request.put(`/api/v1/admin/gifts/${selectedGift.value.id}/stock`, { stock: newStock.value });
    showStockModal.value = false;
    fetchGifts();
  } catch (error) {
    console.error('修改库存失败:', error);
  }
};

const deleteGift = async (gift: Gift) => {
  if (!confirm(`确定要删除礼品"${gift.name}"吗？此操作不可恢复。`)) return;
  try {
    await request.delete(`/api/v1/admin/gifts/${gift.id}`);
    fetchGifts();
  } catch (error) {
    console.error('删除礼品失败:', error);
  }
};

const formatDate = (date: string) => {
  return new Date(date).toLocaleString('zh-CN');
};

onMounted(() => {
  fetchGifts();
  fetchTeachers();
  fetchClasses();
});
</script>
