<template>
  <div class="space-y-6">
    <div class="bg-white shadow rounded-lg p-6">
      <h1 class="text-2xl font-bold text-gray-900 mb-6">我的订单</h1>
      
      <!-- 状态筛选 -->
      <div class="mb-6">
        <h2 class="text-lg font-semibold text-gray-800 mb-4">状态筛选</h2>
        <div class="flex flex-wrap gap-2">
          <button 
            v-for="status in orderStatuses"
            :key="status.value"
            @click="selectStatus(status.value)"
            :class="{
              'px-3 py-1 rounded-full text-xs font-medium': true,
              'bg-primary-100 text-primary-800': selectedStatus === status.value,
              'bg-gray-100 text-gray-800': selectedStatus !== status.value
            }"
          >
            {{ status.label }}
          </button>
        </div>
      </div>

      <div class="mb-4">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-lg font-semibold text-gray-800">兑换记录</h2>
          <button 
            @click="goToShop"
            class="px-4 py-1 bg-primary-600 text-white text-sm rounded-md hover:bg-primary-700 transition-colors"
          >
            去兑换
          </button>
        </div>
        <div class="space-y-3">
          <div v-for="(order, index) in filteredOrders" :key="index" class="border border-gray-200 rounded-lg p-4">
            <div class="flex justify-between items-start">
              <div>
                <h3 class="text-sm font-medium text-gray-900 mb-1">{{ order.gift_name }}</h3>
                <p class="text-xs text-gray-500 mb-1">数量: {{ order.quantity || 1 }}</p>
                <p class="text-xs text-gray-500">兑换时间: {{ new Date(order.created_at).toLocaleString() }}</p>
              </div>
              <div class="text-right">
                <p class="text-sm font-semibold text-gray-900 mb-1">{{ order.price }} 成长值</p>
                <span 
                  :class="{
                    'px-2 py-1 text-xs rounded-full': true,
                    'bg-blue-100 text-blue-800': order.status === 1,
                    'bg-yellow-100 text-yellow-800': order.status === 0,
                    'bg-green-100 text-green-800': order.status === 2,
                  }"
                >
                  {{ order.status === 1 ? '待核销' : order.status === 0 ? '待审核' : '已完成' }}
                </span>
              </div>
            </div>
            
            <!-- 核销码显示 -->
            <div v-if="order.status === 1 && order.qr_code" class="mt-3 p-3 bg-yellow-50 rounded-lg">
              <p class="text-xs font-medium text-gray-800 mb-1">核销码</p>
              <p class="text-sm font-semibold text-yellow-800">{{ order.qr_code }}</p>
              <p class="text-xs text-gray-500 mt-1">请向导师出示此码进行核销</p>
            </div>
            
            <div class="mt-3">
              <button 
                v-if="order.status === 0"
                @click="cancelOrder(order.id)"
                class="text-xs text-primary-600 hover:text-primary-800"
              >
                取消订单
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import request from '@/api/request';
import { onMounted, ref, computed } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

const orders = ref<any[]>([]);
const selectedStatus = ref('all');

// 订单状态选项
const orderStatuses = [
  { label: '全部', value: 'all' },
  { label: '待审核', value: 'pending' },
  { label: '待核销', value: 'approved' },
  { label: '已完成', value: 'completed' },
];

// 计算属性：筛选后的订单
const filteredOrders = computed(() => {
  if (selectedStatus.value === 'all') {
    return orders.value;
  }
  // 映射状态字符串到数字
  const statusMap = {
    'pending': 0,
    'approved': 1,
    'completed': 2,
    'cancelled': 3
  };
  const statusValue = statusMap[selectedStatus.value];
  return orders.value.filter(order => order.status === statusValue);
});

const fetchOrders = async () => {
  try {
    const response = await request.get('/api/v1/orders/user');
    if (response && response.items) {
      orders.value = response.items;
    }
  } catch (error) {
    console.error('获取订单列表失败:', error);
  }
};

const selectStatus = (status: string) => {
  selectedStatus.value = status;
};

const cancelOrder = async (orderId: number) => {
  try {
    await request.post(`/api/v1/order/${orderId}/cancel`);
    await fetchOrders();
    alert('订单已取消');
  } catch (error) {
    console.error('取消订单失败:', error);
    alert('取消订单失败，请稍后重试');
  }
};

const goToShop = () => {
  router.push('/student/shop');
};

onMounted(async () => {
  await fetchOrders();
});
</script>