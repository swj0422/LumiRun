<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-900">兑换管理</h1>
      <button
        @click="showRedemptionModal = true"
        class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
      >
        给学生兑换
      </button>
    </div>

    <!-- 标签页切换 -->
    <div class="bg-white rounded-lg shadow">
      <div class="border-b border-gray-200">
        <nav class="flex -mb-px">
          <button
            @click="activeTab = 'pending'"
            :class="{
              'border-blue-500 text-blue-600': activeTab === 'pending',
              'border-transparent text-gray-500 hover:text-gray-700': activeTab !== 'pending'
            }"
            class="px-6 py-3 text-sm font-medium border-b-2"
          >
            待处理 ({{ pendingCount }})
          </button>
          <button
            @click="switchToCompleted"
            :class="{
              'border-blue-500 text-blue-600': activeTab === 'completed',
              'border-transparent text-gray-500 hover:text-gray-700': activeTab !== 'completed'
            }"
            class="px-6 py-3 text-sm font-medium border-b-2"
          >
            已完成 ({{ completedCount }})
          </button>
        </nav>
      </div>

      <!-- 待处理页面 -->
      <div v-if="activeTab === 'pending'" class="p-4">
        <div class="flex flex-wrap gap-4 mb-4">
          <select
            v-model="selectedClass"
            class="w-48 px-3 py-2 border border-gray-300 rounded-md"
            @change="fetchOrders"
          >
            <option value="">全部班级</option>
            <option v-for="cls in classes" :key="cls.id" :value="cls.id">
              {{ cls.class_name }}
            </option>
          </select>
        </div>

        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                学员
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                奖励
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                班级
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                消耗积分
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                状态
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                操作人
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                时间
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                操作
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="order in orders" :key="order.id">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ order.student_name }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ order.gift_name }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ order.class_name }}
              </td>
              <td
                class="px-6 py-4 whitespace-nowrap text-sm font-medium text-blue-600"
              >
                {{ order.price }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="getStatusClass(order.status)"
                  class="px-2 py-1 text-xs rounded-full"
                >
                  {{ getStatusText(order.status) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ order.operator_name || '-' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(order.created_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm">
                <template v-if="order.status === 0">
                  <button
                    @click="approveOrder(order)"
                    class="text-green-600 hover:text-green-700 mr-3"
                  >
                  通过
                </button>
                <button
                  @click="rejectOrder(order)"
                  class="text-red-600 hover:text-red-700"
                >
                  拒绝
                </button>
              </template>
              <template v-else-if="order.status === 1">
                <button
                  @click="verifyOrder(order)"
                  class="text-blue-600 hover:text-blue-700"
                >
                  核销
                </button>
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

    <!-- 已完成页面 -->
    <div v-if="activeTab === 'completed'" class="p-4">
      <div class="flex flex-wrap gap-4 mb-4">
        <select
          v-model="selectedCompletedClass"
          class="w-48 px-3 py-2 border border-gray-300 rounded-md"
          @change="fetchCompletedOrders"
        >
          <option value="">全部班级</option>
          <option v-for="cls in classes" :key="cls.id" :value="cls.id">
            {{ cls.class_name }}
          </option>
        </select>
      </div>

      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              学员
            </th>
            <th
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              奖励
            </th>
            <th
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              班级
            </th>
            <th
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              消耗积分
            </th>
            <th
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              状态
            </th>
            <th
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              操作人
            </th>
            <th
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              操作时间
            </th>
            <th
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              备注
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="order in completedOrders" :key="order.id">
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              {{ order.student_name }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ order.gift_name }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ order.class_name }}
            </td>
            <td
              class="px-6 py-4 whitespace-nowrap text-sm font-medium text-blue-600"
            >
              {{ order.price }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span
                :class="getCompletedStatusClass(order.status)"
                class="px-2 py-1 text-xs rounded-full"
              >
                {{ getCompletedStatusText(order.status) }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ order.operator_name || '-' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ formatDate(order.operated_at) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ order.remarks || '-' }}
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="completedOrders.length === 0" class="text-center py-12">
        <p class="text-gray-500">暂无已完成订单数据</p>
      </div>
    </div>
  </div>

    <div
      v-if="showRejectModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 class="text-xl font-bold mb-4">拒绝原因</h2>
        <form @submit.prevent="handleReject">
          <div>
            <textarea
              v-model="rejectReason"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md"
              rows="3"
              placeholder="请输入拒绝原因"
            ></textarea>
          </div>
          <div class="flex justify-end space-x-3 mt-6">
            <button
              type="button"
              @click="showRejectModal = false"
              class="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300"
            >
              取消
            </button>
            <button
              type="submit"
              class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              确认
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 给学生兑换弹窗 -->
    <div
      v-if="showRedemptionModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 class="text-xl font-bold mb-4">学员兑换奖励</h2>
        <form @submit.prevent="submitRedemption">
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                选择班级 <span class="text-red-500">*</span>
              </label>
              <select
                v-model="redemptionForm.classId"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md"
                @change="handleClassChange"
              >
                <option value="">请选择班级</option>
                <option v-for="cls in classes" :key="cls.id" :value="cls.id">
                  {{ cls.school_name }} - {{ cls.session }} -
                  {{ cls.class_name }}
                </option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                选择学生 <span class="text-red-500">*</span>
              </label>
              <div class="relative">
                <input
                  type="text"
                  v-model="studentSearch"
                  placeholder="输入学生姓名搜索..."
                  class="w-full px-3 py-2 border border-gray-300 rounded-md"
                  @focus="showStudentDropdown = true"
                  @blur="handleBlur"
                />
                <div
                  v-if="showStudentDropdown && filteredStudents.length > 0"
                  class="absolute z-10 w-full max-h-60 overflow-y-auto bg-white border border-gray-300 rounded-md shadow-lg"
                >
                  <div
                    v-for="student in filteredStudents"
                    :key="student.id"
                    class="px-3 py-2 hover:bg-gray-100 cursor-pointer"
                    @mousedown="
                      () => {
                        redemptionForm.studentId = String(student.id);
                        studentSearch = student.real_name;
                        showStudentDropdown = false;
                        handleStudentChange();
                      }
                    "
                  >
                    {{ student.real_name }} ({{ student.available_score }} 积分)
                  </div>
                </div>
                <div
                  v-else-if="
                    showStudentDropdown && filteredStudents.length === 0
                  "
                  class="absolute z-10 w-full bg-white border border-gray-300 rounded-md shadow-lg p-3 text-gray-500"
                >
                  未找到匹配的学生
                </div>
                <input type="hidden" v-model="redemptionForm.studentId" />
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                选择奖励 <span class="text-red-500">*</span>
              </label>
              <div class="text-xs text-gray-500 mb-1">
                可用奖励数量: {{ availableGifts.length }}
                <span v-if="availableGifts.length > 0">
                  ({{ availableGifts.map((g) => g.name).join(', ') }})
                </span>
              </div>
              <select
                v-model="redemptionForm.giftId"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md mb-3"
              >
                <option value="">请选择奖励</option>
                <option
                  v-for="gift in availableGifts"
                  :key="gift.id"
                  :value="gift.id"
                >
                  {{ gift.name }} ({{ gift.price }} 积分)
                </option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                兑换份数
                <span class="text-red-500"
                  >*（最多可兑换 {{ getMaxQuantity() }} 份）</span
                >
                <span
                  v-if="selectedGift && selectedStudent"
                  class="text-xs text-gray-500 ml-2"
                >
                </span>
              </label>
              <div class="text-xs text-gray-500 mb-1">
                <span v-if="selectedGift && selectedStudent">
                  库存: {{ selectedGift.stock }} | 学员可用积分:
                  {{ selectedStudent.available_score }} | 所需积分:
                  {{ selectedGift.price * redemptionForm.quantity }} |
                  最多可兑换: {{ getMaxQuantity() }} 份
                </span>
              </div>
              <input
                type="number"
                v-model.number="redemptionForm.quantity"
                required
                min="1"
                :max="getMaxQuantity()"
                class="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>
          </div>
          <div class="flex justify-end space-x-3 mt-6">
            <button
              type="button"
              @click="showRedemptionModal = false"
              class="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300"
            >
              取消
            </button>
            <button
              type="submit"
              class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              确定兑换
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 核销弹窗 -->
    <div
      v-if="showVerifyModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 class="text-xl font-bold mb-4">核销订单</h2>
        <form @submit.prevent="handleVerify">
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">
              核销码
            </label>
            <div class="flex gap-2">
              <input
                type="text"
                v-model="verifyCode"
                required
                class="flex-1 px-3 py-2 border border-gray-300 rounded-md"
                placeholder="请输入核销码"
              />
              <button
                type="button"
                @click="scanQRCode"
                class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
              >
                扫码
              </button>
            </div>
          </div>
          
          <!-- 扫码区域 -->
          <div v-if="showScanArea" class="mb-4">
            <div class="border-2 border-dashed border-gray-300 rounded-md p-4">
              <div id="qr-reader" class="w-full h-48 bg-gray-100 rounded"></div>
              <p class="text-center text-sm text-gray-500 mt-2">请将二维码对准扫描框</p>
            </div>
          </div>
          
          <div class="flex justify-end space-x-3 mt-6">
            <button
              type="button"
              @click="showVerifyModal = false"
              class="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300"
            >
              取消
            </button>
            <button
              type="submit"
              class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              确认核销
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import request from '@/api/request';
import { onActivated, onMounted, ref, watch, computed } from 'vue';

interface Order {
  id: number;
  student_name: string;
  gift_name: string;
  class_name: string;
  price: number;
  status: number;
  created_at: string;
  operator_name?: string;
}

interface ClassInfo {
  id: number;
  class_name: string;
  school_name?: string;
  session?: string;
}

interface Student {
  id: string | number;
  real_name: string;
  available_score: number;
}

interface Gift {
  id: number;
  name: string;
  price: number;
  stock: number;
  status: boolean;
}

const orders = ref<Order[]>([]);
const completedOrders = ref<Order[]>([]);
const classes = ref<ClassInfo[]>([]);
const students = ref<Student[]>([]);
const availableGifts = ref<Gift[]>([]);
const selectedGift = ref<Gift | null>(null);
const selectedStudent = ref<Student | null>(null);
const selectedClass = ref('');
const selectedCompletedClass = ref('');
const selectedStatus = ref('');
const activeTab = ref('pending');
const pendingCount = ref(0);
const completedCount = ref(0);
const showRejectModal = ref(false);
const showRedemptionModal = ref(false);
const showVerifyModal = ref(false);
const showScanArea = ref(false);
const rejectReason = ref('');
const verifyCode = ref('');
const selectedOrder = ref<Order | null>(null);
const selectedVerifyOrder = ref<Order | null>(null);
let qrCodeScanner: any = null;
const redemptionForm = ref({
  classId: '',
  studentId: '',
  giftId: '',
  quantity: 1,
});
const studentSearch = ref('');
const showStudentDropdown = ref(false);

// 过滤学生列表（搜索）
const filteredStudents = computed(() => {
  let result = students.value;

  if (studentSearch.value) {
    const searchTerm = studentSearch.value.toLowerCase();
    result = result.filter((student) =>
      student.real_name.toLowerCase().includes(searchTerm)
    );
  }

  return result;
});

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
    console.log('获取班级列表失败，显示空列表');
  }
};

const fetchOrders = async () => {
  try {
    const params: Record<string, any> = {};
    if (selectedClass.value) {
      params.class_id = selectedClass.value;
    }
    if (selectedStatus.value) {
      params.status = selectedStatus.value;
    }
    console.log('请求订单列表:', '/v1/orders/', params);
    const data = (await request.get('/api/v1/orders/', { params })) as {
      items: Order[];
    };
    console.log('获取到的订单列表:', data);
    orders.value = data.items || [];
    pendingCount.value = orders.value.filter(o => o.status === 0 || o.status === 1).length;
  } catch (error) {
    orders.value = [];
    console.log('获取订单列表失败，显示空列表', error);
  }
};

const switchToCompleted = async () => {
  activeTab.value = 'completed';
  await fetchCompletedOrders();
};

const fetchCompletedOrders = async () => {
  try {
    const params: Record<string, any> = {};
    if (selectedCompletedClass.value) {
      params.class_id = selectedCompletedClass.value;
    }
    const data = (await request.get('/api/v1/orders/completed', { params })) as {
      items: any[];
    };
    completedOrders.value = data.items || [];
    completedCount.value = completedOrders.value.length;
  } catch (error) {
    completedOrders.value = [];
    console.log('获取已完成订单列表失败，显示空列表', error);
  }
};

const approveOrder = async (order: Order) => {
  try {
    await request.post(`/api/v1/orders/${order.id}/approve`);
    fetchOrders();
  } catch (error) {
    console.error('审核通过失败:', error);
  }
};

const rejectOrder = (order: Order) => {
  selectedOrder.value = order;
  rejectReason.value = '';
  showRejectModal.value = true;
};

const verifyOrder = (order: Order) => {
  selectedVerifyOrder.value = order;
  verifyCode.value = '';
  showVerifyModal.value = true;
};

const scanQRCode = async () => {
  showScanArea.value = !showScanArea.value;
  
  if (showScanArea.value) {
    try {
      const { Html5Qrcode } = await import('html5-qrcode');
      
      qrCodeScanner = new Html5Qrcode('qr-reader');
      
      qrCodeScanner.start(
        { facingMode: 'environment' },
        {
          fps: 10,
          qrbox: { width: 250, height: 250 },
        },
        (decodedText: string, decodedResult: any) => {
          verifyCode.value = decodedText;
          stopScan();
        },
        (errorMessage: string) => {
          // 扫描失败时的回调，可以忽略
        }
      ).catch((err: any) => {
        console.error('扫码启动失败:', err);
        alert('扫码启动失败，请确保已授权摄像头权限');
        showScanArea.value = false;
      });
    } catch (error) {
      console.error('加载扫码库失败:', error);
      alert('扫码功能不可用');
      showScanArea.value = false;
    }
  } else {
    stopScan();
  }
};

const stopScan = () => {
  if (qrCodeScanner) {
    qrCodeScanner.stop().catch((err: any) => {
      console.error('停止扫码失败:', err);
    });
    qrCodeScanner = null;
  }
  showScanArea.value = false;
};

const handleVerify = async () => {
  stopScan();
  
  try {
    if (!selectedVerifyOrder.value) return;
    
    await request.post(`/api/v1/orders/${selectedVerifyOrder.value.id}/verify`, {
      qr_code: verifyCode.value
    });
    showVerifyModal.value = false;
    await fetchOrders();
    alert('核销成功');
  } catch (error: any) {
    console.error('核销失败:', error);
    const errorDetail = error?.response?.data?.detail;
    const errorMessage = Array.isArray(errorDetail) ? errorDetail.join(', ') : (errorDetail || '核销失败，请稍后重试');
    alert('核销失败：' + errorMessage);
  }
};

const handleReject = async () => {
  try {
    if (!selectedOrder.value) return;
    await request.post(`/api/v1/orders/${selectedOrder.value.id}/reject`, {
      reason: rejectReason.value,
    });
    showRejectModal.value = false;
    fetchOrders();
  } catch (error) {
    console.error('拒绝订单失败:', error);
  }
};

const getStatusClass = (status: number) => {
  switch (status) {
    case 0:
      return 'bg-yellow-100 text-yellow-800';
    case 1:
      return 'bg-blue-100 text-blue-800';
    case 2:
      return 'bg-green-100 text-green-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

const getStatusText = (status: number) => {
  switch (status) {
    case 0:
      return '待审核';
    case 1:
      return '待核销';
    case 2:
      return '已完成';
    default:
      return '未知';
  }
};

const getCompletedStatusClass = (status: number) => {
  switch (status) {
    case 2:
      return 'bg-green-100 text-green-800';
    case 3:
      return 'bg-red-100 text-red-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

const getCompletedStatusText = (status: number) => {
  switch (status) {
    case 2:
      return '已完成';
    case 3:
      return '已取消';
    default:
      return '未知';
  }
};

const formatDate = (date: string) => {
  return new Date(date).toLocaleString('zh-CN');
};

const handleClassChange = async () => {
  console.log('handleClassChange 被调用');
  console.log('redemptionForm.value:', redemptionForm.value);

  if (!redemptionForm.value.classId) {
    console.log('classId 为空');
    students.value = [];
    redemptionForm.value.studentId = '';
    availableGifts.value = [];
    redemptionForm.value.giftId = '';
    return;
  }

  try {
    console.log('开始获取班级学生和奖励');
    const classId = parseInt(redemptionForm.value.classId as string);
    console.log('转换后的 classId:', classId);

    // 获取班级学生列表
    const data = (await request.get(`/api/v1/classes/${classId}/students`)) as {
      items: Student[];
    };
    console.log('获取到的学生列表:', data);
    if (data && data.items) {
      students.value = data.items.map((item: any) => ({
        id: item.id,
        real_name: item.real_name,
        available_score: item.available_score || 0,
      }));
    } else {
      students.value = [];
    }
    redemptionForm.value.studentId = '';

    // 获取班级可用的奖励列表
    console.log('请求礼品列表接口:', `/v1/gifts/class/${classId}`);
    const giftData = (await request.get(`/api/v1/gifts/class/${classId}`)) as {
      items: Gift[];
    };
    console.log('获取到的奖励列表:', giftData);
    availableGifts.value = giftData.items || [];
    console.log('availableGifts.value:', availableGifts.value);
    console.log('礼品数量:', availableGifts.value.length);
    redemptionForm.value.giftId = '';
  } catch (error) {
    console.error('获取班级学生失败:', error);
    students.value = [];
    availableGifts.value = [];
  }
};

const handleStudentChange = async () => {
  console.log('handleStudentChange 被调用');
  console.log('redemptionForm.value:', redemptionForm.value);

  if (!redemptionForm.value.studentId || !redemptionForm.value.classId) {
    console.log('studentId 或 classId 为空');
    availableGifts.value = [];
    redemptionForm.value.giftId = '';
    return;
  }

  try {
    console.log('开始获取可用奖励');
    const classId = parseInt(redemptionForm.value.classId as string);
    console.log('转换后的 classId:', classId);
    // 获取学生可用的奖励列表
    const data = (await request.get(`/api/v1/gifts/class/${classId}`)) as {
      items: Gift[];
    };
    console.log('获取到的奖励列表:', data);
    availableGifts.value = data.items || [];
    console.log('availableGifts.value:', availableGifts.value);
    redemptionForm.value.giftId = '';
  } catch (error) {
    console.error('获取可用奖励失败:', error);
    availableGifts.value = [];
  }
};

// 处理输入框失焦
const handleBlur = () => {
  setTimeout(() => {
    showStudentDropdown.value = false;
  }, 200);
};

// 监听学生选择变化，更新选中的学生信息
watch(
  () => redemptionForm.value.studentId,
  (studentId) => {
    if (studentId) {
      selectedStudent.value =
        students.value.find((student) => {
          return String(student.id) === String(studentId);
        }) || null;
    } else {
      selectedStudent.value = null;
    }
  }
);

// 监听礼品选择变化，更新选中的礼品信息
watch(
  () => redemptionForm.value.giftId,
  (giftId) => {
    if (giftId) {
      selectedGift.value =
        availableGifts.value.find((gift) => {
          return gift.id === parseInt(giftId);
        }) || null;
    } else {
      selectedGift.value = null;
    }
    // 重置兑换份数
    redemptionForm.value.quantity = 1;
  }
);

// 监听学生选择变化，重置兑换份数
watch(
  () => redemptionForm.value.studentId,
  () => {
    redemptionForm.value.quantity = 1;
  }
);

// 计算最大可兑换数量
const getMaxQuantity = () => {
  if (!selectedGift.value || !selectedStudent.value) {
    return 0;
  }

  // 计算库存限制
  const stockLimit = selectedGift.value.stock;

  // 计算成长值限制
  const growthLimit = Math.floor(
    selectedStudent.value.available_score / selectedGift.value.price
  );

  // 取最小值，确保至少为 0
  return Math.max(0, Math.min(stockLimit, growthLimit));
};

const submitRedemption = async () => {
  try {
    console.log('开始兑换，表单数据:', redemptionForm.value);
    console.log('students.value:', students.value);

    // 检查是否选择了班级
    if (!redemptionForm.value.classId) {
      alert('请选择班级');
      return;
    }

    // 检查是否选择了学生
    if (!redemptionForm.value.studentId) {
      alert('请选择学生');
      return;
    }

    // 检查是否选择了礼品
    if (!redemptionForm.value.giftId) {
      alert('请选择礼品');
      return;
    }

    // 检查兑换数量是否超过最大可兑换数量
    const maxQuantity = getMaxQuantity();
    if (redemptionForm.value.quantity > maxQuantity) {
      alert('兑换数量超过最大可兑换数量');
      return;
    }

    // 移除绑定检查，所有有积分的学生都可以兑换
    // if (typeof redemptionForm.value.studentId === 'string' && redemptionForm.value.studentId.startsWith('temp_')) {
    //   alert('该学生尚未绑定用户账号，无法进行兑换')
    //   return
    // }

    // 构建兑换数据
    console.log(
      'redemptionForm.value.studentId:',
      redemptionForm.value.studentId
    );
    console.log(
      'typeof redemptionForm.value.studentId:',
      typeof redemptionForm.value.studentId
    );

    const giftId = redemptionForm.value.giftId
      ? parseInt(redemptionForm.value.giftId as string)
      : NaN;
    const classId = redemptionForm.value.classId
      ? parseInt(redemptionForm.value.classId as string)
      : NaN;

    // 处理学生ID，支持temp_开头的临时ID
    let studentId: any = null;
    if (redemptionForm.value.studentId) {
      studentId = redemptionForm.value.studentId;
    }

    const quantity = redemptionForm.value.quantity;

    console.log('转换后的参数:', { giftId, classId, studentId, quantity });
    console.log('参数类型:', {
      giftId: typeof giftId,
      classId: typeof classId,
      studentId: typeof studentId,
      quantity: typeof quantity,
    });
    console.log('是否为有效参数:', {
      giftId: !isNaN(giftId),
      classId: !isNaN(classId),
      studentId: !!studentId,
      quantity: !isNaN(quantity),
    });

    // 检查参数是否有效
    if (!redemptionForm.value.giftId || isNaN(giftId)) {
      alert('礼品选择错误，请重新选择');
      return;
    }

    if (!redemptionForm.value.classId || isNaN(classId)) {
      alert('班级选择错误，请重新选择');
      return;
    }

    if (!redemptionForm.value.studentId || !studentId) {
      alert('学生选择错误，请重新选择');
      return;
    }

    if (isNaN(quantity) || quantity <= 0) {
      alert('兑换数量错误，请输入有效数量');
      return;
    }

    const redemptionData = {
      gift_id: giftId,
      class_id: classId,
      user_id: studentId,
      quantity: quantity,
    };

    console.log('兑换数据:', redemptionData);

    // 调用兑换接口
    await request.post('/api/v1/orders/teacher', redemptionData);

    // 关闭弹窗并刷新订单列表
    showRedemptionModal.value = false;
    await fetchOrders();
  } catch (error) {
    console.error('兑换失败:', error);
  }
};

onMounted(async () => {
  await fetchClasses();
  await fetchOrders();
  await fetchCompletedOrders();
});

onActivated(async () => {
  await fetchClasses();
  await fetchOrders();
  await fetchCompletedOrders();
});
</script>
