<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-900">订单管理</h1>
    </div>

    <div class="bg-white rounded-lg shadow p-4">
      <div class="flex flex-wrap gap-4">
        <select v-model="selectedClass" class="input w-48" @change="fetchOrders">
          <option value="">全部组织</option>
          <option v-for="cls in classes" :key="cls.id" :value="cls.id">{{ cls.class_name }}</option>
        </select>
        <select v-model="selectedStatus" class="input w-32" @change="fetchOrders">
          <option value="">全部状态</option>
          <option value="0">待核销</option>
          <option value="1">已核销</option>
          <option value="2">已取消</option>
        </select>
        <input
          v-model="startTime"
          type="date"
          class="input w-40"
          @change="fetchOrders"
        />
        <span class="text-gray-500 self-center">至</span>
        <input
          v-model="endTime"
          type="date"
          class="input w-40"
          @change="fetchOrders"
        />
      </div>
    </div>

    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">成员</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">组织</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">礼品名称</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">消耗积分</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
            
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">时间</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="order in orders" :key="order.id">
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ order.student_name }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ order.class_name }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ order.gift_name }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-primary-600">{{ order.points_cost }}</td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="getStatusClass(order.status)" class="px-2 py-1 text-xs rounded-full">
                {{ getStatusText(order.status) }}
              </span>
            </td>
            
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ formatDate(order.created_at) }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
              <template v-if="order.status === 1">
                <button @click="verifyOrder(order.id)" class="text-green-600 hover:text-green-700 mr-2">核销</button>
                <button @click="cancelOrder(order)" class="text-red-600 hover:text-red-700">取消</button>
              </template>
              <template v-else-if="order.status === 0">
                <button @click="cancelOrder(order)" class="text-red-600 hover:text-red-700">取消</button>
              </template>
              <span v-else class="text-gray-400">-</span>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="orders.length === 0" class="text-center py-12">
        <p class="text-gray-500">暂无订单数据</p>
      </div>
    </div>

    <div v-if="showCancelModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
        <h2 class="text-xl font-bold mb-4">取消订单确认</h2>
        <div class="space-y-4">
          <p class="text-gray-600">确定要取消该订单吗？取消后将返还 <span class="font-bold text-primary-600">{{ selectedOrder?.points_cost }}</span> 成长值给成员。</p>
          <div class="flex justify-end gap-2">
            <button @click="showCancelModal = false" class="btn-secondary">取消</button>
            <button @click="confirmCancel" class="btn-primary">确认取消</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import request from '@/api/request';
import { onMounted, ref } from 'vue';

interface Order {
  id: number;
  student_name: string;
  class_name: string;
  gift_name: string;
  points_cost: number;
  status: number;
  verify_code: string;
  created_at: string;
}

interface ClassInfo {
  id: number;
  class_name: string;
}

const orders = ref<Order[]>([]);
const classes = ref<ClassInfo[]>([]);
const selectedClass = ref('');
const selectedStatus = ref('');
const startTime = ref('');
const endTime = ref('');
const showCancelModal = ref(false);
const selectedOrder = ref<Order | null>(null);

const fetchOrders = async () => {
  try {
    const params: Record<string, any> = {};
    if (selectedClass.value) params.class_id = selectedClass.value;
    if (selectedStatus.value) params.status = parseInt(selectedStatus.value);
    if (startTime.value) params.start_time = startTime.value + 'T00:00:00';
    if (endTime.value) params.end_time = endTime.value + 'T23:59:59';
    const data = (await request.get('/api/v1/admin/orders', { params })) as { items: Order[] };
    orders.value = data.items || [];
  } catch (error) {
    console.error('获取订单列表失败:', error);
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

const verifyOrder = async (orderId: number) => {
  if (!confirm('确定要核销该订单吗？')) return;
  try {
    await request.post(`/api/v1/admin/orders/${orderId}/verify`);
    fetchOrders();
  } catch (error) {
    console.error('核销订单失败:', error);
  }
};

const cancelOrder = (order: Order) => {
  selectedOrder.value = order;
  showCancelModal.value = true;
};

const confirmCancel = async () => {
  if (!selectedOrder.value) return;
  try {
    await request.post(`/api/v1/admin/orders/${selectedOrder.value.id}/cancel`);
    showCancelModal.value = false;
    fetchOrders();
  } catch (error) {
    console.error('取消订单失败:', error);
  }
};

const getStatusClass = (status: number): string => {
  const classes: Record<number, string> = {
    0: 'bg-yellow-100 text-yellow-800',
    1: 'bg-blue-100 text-blue-800',
    2: 'bg-green-100 text-green-800',
    3: 'bg-red-100 text-red-800',
  };
  return classes[status] || 'bg-gray-100 text-gray-800';
};

const getStatusText = (status: number): string => {
  const statusMap: Record<number, string> = {
    0: '待审核',
    1: '待核销',
    2: '已完成',
    3: '已取消',
  };
  return statusMap[status] || '未知';
};

const formatDate = (date: string) => {
  return new Date(date).toLocaleString('zh-CN');
};

onMounted(() => {
  fetchOrders();
  fetchClasses();
});
</script>
