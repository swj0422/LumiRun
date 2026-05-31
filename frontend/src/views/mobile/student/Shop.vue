<template>
  <div class="space-y-6">
    <div class="bg-white shadow rounded-lg p-6">
      <h1 class="text-2xl font-bold text-gray-900 mb-6">奖励兑换</h1>

      <div class="mb-6">
        <h2 class="text-lg font-semibold text-gray-800 mb-4">可用成长值</h2>
        <div class="bg-primary-50 rounded-lg p-4">
          <p class="text-2xl font-bold text-primary-800">{{ growthScore.available_score }}</p>
        </div>
      </div>

      <!-- 兑换规则说明 -->
      <div class="mb-6 p-4 bg-blue-50 rounded-lg">
        <h2 class="text-lg font-semibold text-gray-800 mb-2">兑换规则</h2>
        <ul class="text-sm text-gray-600 space-y-2">
          <li class="flex items-start">
            <svg class="w-4 h-4 text-blue-600 mt-0.5 mr-2 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            每个礼品需要消耗相应的成长值
          </li>
          <li class="flex items-start">
            <svg class="w-4 h-4 text-blue-600 mt-0.5 mr-2 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            兑换后请等待管理者审核
          </li>
          <li class="flex items-start">
            <svg class="w-4 h-4 text-blue-600 mt-0.5 mr-2 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            审核通过后，可在"我的订单"中查看核销码
          </li>
          <li class="flex items-start">
            <svg class="w-4 h-4 text-blue-600 mt-0.5 mr-2 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            库存不足时无法兑换
          </li>
        </ul>
      </div>

      <div class="mb-4">
        <h2 class="text-lg font-semibold text-gray-800 mb-4">可用奖励</h2>
        <div v-if="loading" class="text-center py-8">
          <p class="text-gray-500">加载中...</p>
        </div>
        <div v-else-if="gifts.length === 0" class="text-center py-8">
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          <h3 class="mt-2 text-sm font-medium text-gray-900">暂无可兑换的奖励</h3>
          <p class="mt-1 text-sm text-gray-500">当前组织暂无开放兑换的奖励</p>
        </div>
        <div v-else class="grid grid-cols-4 gap-3">
          <div
            v-for="gift in gifts"
            :key="gift.id"
            class="bg-white rounded-lg shadow overflow-hidden border border-gray-200"
          >
            <div class="aspect-w-16 aspect-h-9 bg-gray-200">
              <img
                v-if="gift.image_path"
                :src="gift.image_path"
                :alt="gift.name"
                class="w-full h-32 object-cover"
              />
              <div
                v-else
                class="w-full h-32 flex items-center justify-center text-gray-400"
              >
                <svg
                  class="w-10 h-10"
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
              <h3 class="text-lg font-semibold text-gray-900 mb-2 truncate">
                {{ gift.name }}
              </h3>
              <p class="text-sm text-gray-500 mb-3 line-clamp-2">
                {{ gift.description || '暂无描述' }}
              </p>
              <div class="flex justify-between items-center mb-3">
                <span class="text-blue-600 font-bold">{{ gift.price }} 成长值</span>
                <span
                  :class="gift.stock > 0 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                  class="px-2 py-1 text-xs rounded-full"
                >
                  {{ gift.stock > 0 ? `库存: ${gift.stock}` : '缺货' }}
                </span>
              </div>
              <button
                @click="openExchangeDialog(gift)"
                :disabled="gift.stock === 0 || growthScore.available_score < gift.price"
                class="w-full py-2 text-sm rounded-md"
                :class="{
                  'bg-primary-600 text-white hover:bg-primary-700': gift.stock > 0 && growthScore.available_score >= gift.price,
                  'bg-gray-300 text-gray-500 cursor-not-allowed': gift.stock === 0 || growthScore.available_score < gift.price
                }"
              >
                {{ gift.stock === 0 ? '缺货' : growthScore.available_score < gift.price ? '成长值不足' : '兑换' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 兑换数量选择弹窗 -->
    <div v-if="showExchangeDialog" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-80 max-w-full mx-4">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">选择兑换数量</h3>
        <div class="mb-4">
          <p class="text-sm text-gray-600 mb-2">礼品：{{ selectedGift?.name }}</p>
          <p class="text-sm text-gray-600 mb-2">单价：{{ selectedGift?.price }} 成长值</p>
          <p class="text-sm text-gray-600 mb-4">库存：{{ selectedGift?.stock }}</p>
          <div class="flex items-center justify-between">
            <span class="text-sm text-gray-600">数量：</span>
            <div class="flex items-center">
              <button 
                @click="decreaseQuantity"
                class="w-8 h-8 bg-gray-200 rounded-md flex items-center justify-center hover:bg-gray-300"
                :disabled="exchangeQuantity <= 1"
              >
                <span class="text-gray-600 font-bold">-</span>
              </button>
              <input 
                type="number" 
                v-model="exchangeQuantity" 
                min="1" 
                :max="selectedGift?.stock"
                class="w-16 h-8 text-center border border-gray-300 rounded-md mx-2"
                @input="validateQuantity"
              />
              <button 
                @click="increaseQuantity"
                class="w-8 h-8 bg-gray-200 rounded-md flex items-center justify-center hover:bg-gray-300"
                :disabled="exchangeQuantity >= selectedGift?.stock"
              >
                <span class="text-gray-600 font-bold">+</span>
              </button>
            </div>
          </div>
          <p class="text-sm text-gray-600 mt-4">
            合计：<span class="text-primary-600 font-bold">{{ selectedGift?.price * exchangeQuantity }}</span> 成长值
          </p>
          <p v-if="selectedGift?.price * exchangeQuantity > growthScore.available_score" class="text-sm text-red-500 mt-2">
            成长值不足，无法兑换
          </p>
        </div>
        <div class="flex justify-end gap-2">
          <button 
            @click="closeExchangeDialog"
            class="px-4 py-2 text-sm text-gray-600 hover:text-gray-800"
          >
            取消
          </button>
          <button 
            @click="confirmExchange"
            :disabled="exchangeQuantity < 1 || exchangeQuantity > selectedGift?.stock || selectedGift?.price * exchangeQuantity > growthScore.available_score"
            class="px-4 py-2 text-sm bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            确定
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import request from '@/api/request';
import { onMounted, ref } from 'vue';

const growthScore = ref({
  available_score: 0,
});

const gifts = ref<any[]>([]);
const loading = ref(false);
const currentClassId = ref<number | null>(null);

// 兑换数量选择相关变量
const showExchangeDialog = ref(false);
const selectedGift = ref<any>(null);
const exchangeQuantity = ref(1);

const fetchGrowthScore = async () => {
  try {
    const response = await request.get('/api/v1/growth/score');
    if (response) {
      growthScore.value = {
        available_score: response.available_score,
      };
    }
  } catch (error) {
    console.error('获取成长值失败:', error);
  }
};

const fetchGifts = async () => {
  loading.value = true;
  try {
    // 先获取组织信息
    console.log('[DEBUG] fetchGifts - 开始获取组织信息');
    const classResponse = await request.get('/api/v1/students/my-classes');
    console.log('[DEBUG] fetchGifts - 组织响应:', classResponse);
    if (classResponse && Array.isArray(classResponse) && classResponse.length > 0) {
      currentClassId.value = classResponse[0].class_id;
      console.log('[DEBUG] fetchGifts - 设置 currentClassId:', currentClassId.value);
    } else {
      console.log('[DEBUG] fetchGifts - 未找到组织或响应格式不对');
    }

    // 再获取礼品列表
    const response = await request.get('/api/v1/gifts/student/available');
    console.log('[DEBUG] fetchGifts - 礼品响应:', response);
    if (response && response.items) {
      gifts.value = response.items;
    }
  } catch (error) {
    console.error('获取奖励列表失败:', error);
    gifts.value = [];
  } finally {
    loading.value = false;
  }
};

// 打开兑换弹窗
const openExchangeDialog = (gift: any) => {
  selectedGift.value = gift;
  exchangeQuantity.value = 1;
  showExchangeDialog.value = true;
};

// 关闭兑换弹窗
const closeExchangeDialog = () => {
  showExchangeDialog.value = false;
  selectedGift.value = null;
  exchangeQuantity.value = 1;
};

// 增加数量
const increaseQuantity = () => {
  if (selectedGift.value && exchangeQuantity.value < selectedGift.value.stock) {
    exchangeQuantity.value++;
  }
};

// 减少数量
const decreaseQuantity = () => {
  if (exchangeQuantity.value > 1) {
    exchangeQuantity.value--;
  }
};

// 验证数量输入
const validateQuantity = () => {
  if (!selectedGift.value) return;
  if (exchangeQuantity.value < 1) {
    exchangeQuantity.value = 1;
  }
  if (exchangeQuantity.value > selectedGift.value.stock) {
    exchangeQuantity.value = selectedGift.value.stock;
  }
};

// 确认兑换
const confirmExchange = async () => {
  if (!selectedGift.value || !currentClassId.value) {
    alert('无法获取兑换信息，请刷新页面重试');
    return;
  }
  
  if (selectedGift.value.price * exchangeQuantity.value > growthScore.value.available_score) {
    alert('成长值不足，无法兑换');
    return;
  }
  
  try {
    const response = await request.post('/api/v1/orders/', {
      gift_id: selectedGift.value.id,
      class_id: currentClassId.value,
      quantity: exchangeQuantity.value,
    });
    console.log('[DEBUG] exchangeGift response:', response);
    // 检查响应是否有id或status字段表示成功
    if (response && (response.id || response.status === 0)) {
      alert(`兑换成功！共兑换 ${exchangeQuantity.value} 件，请等待管理者审核。`);
      closeExchangeDialog();
      // 重新获取成长值和奖励列表
      await fetchGrowthScore();
      await fetchGifts();
    } else {
      alert('兑换失败：' + (response?.message || '未知错误'));
    }
  } catch (error: any) {
    console.error('兑换奖励失败:', error);
    const errorDetail = error?.response?.data?.detail;
    const errorMessage = Array.isArray(errorDetail) ? errorDetail.join(', ') : (errorDetail || '请稍后重试');
    alert('兑换失败：' + errorMessage);
  }
};

onMounted(async () => {
  await fetchGrowthScore();
  await fetchGifts();
});
</script>