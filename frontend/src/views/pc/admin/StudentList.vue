<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-900">学员管理</h1>
    </div>

    <div class="bg-white rounded-lg shadow p-4">
      <div class="flex flex-wrap gap-4">
        <input
          v-model="searchKeyword"
          type="text"
          class="input flex-1 min-w-[200px]"
          placeholder="搜索学员姓名"
          @input="handleSearch"
        />
        <select v-model="selectedClass" class="input w-48" @change="fetchStudents">
          <option value="">全部班级</option>
          <option v-for="cls in classes" :key="cls.id" :value="cls.id">{{ cls.class_name }}</option>
        </select>
        <select v-model="selectedBindStatus" class="input w-32" @change="fetchStudents">
          <option value="">全部状态</option>
          <option value="approved">已绑定</option>
          <option value="pending">待审核</option>
          <option value="rejected">已拒绝</option>
        </select>
        <select v-model="selectedIsDeleted" class="input w-32" @change="fetchStudents">
          <option value="">全部</option>
          <option value="false">正常</option>
          <option value="true">已删除</option>
        </select>
      </div>
    </div>

    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">姓名</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">昵称</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">班级</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">绑定状态</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">创建时间</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="student in students" :key="student.id">
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ student.name_in_class || '-' }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ student.name }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ student.class_name }}</td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="getBindStatusClass(student.bind_status)" class="px-2 py-1 text-xs rounded-full">
                {{ getBindStatusText(student.bind_status) }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="student.is_deleted ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'" class="px-2 py-1 text-xs rounded-full">
                {{ student.is_deleted ? '已删除' : '正常' }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ formatDate(student.created_at) }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
              <button @click="viewDetail(student)" class="text-blue-600 hover:text-blue-700 mr-2">详情</button>
              <button @click="viewGrowth(student)" class="text-green-600 hover:text-green-700 mr-2">成长记录</button>
              <button
                v-if="student.bind_status === 'approved'"
                @click="unbindStudent(student)"
                class="text-yellow-600 hover:text-yellow-700 mr-2"
              >
                解绑
              </button>
              <button @click="viewLogs(student)" class="text-purple-600 hover:text-purple-700 mr-2">日志</button>
              <button @click="deleteStudent(student)" class="text-red-600 hover:text-red-700">删除</button>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="students.length === 0" class="text-center py-12">
        <p class="text-gray-500">暂无学员数据</p>
      </div>
    </div>

    <div v-if="showDetailModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
        <h2 class="text-xl font-bold mb-4">学员详情</h2>
        <div class="space-y-3">
          <div class="flex justify-between">
            <span class="text-gray-500">姓名:</span>
            <span class="font-medium">{{ selectedStudent?.name || '-' }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-500">班级昵称:</span>
            <span class="font-medium">{{ selectedStudent?.name_in_class }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-500">班级:</span>
            <span class="font-medium">{{ selectedStudent?.class_name }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-500">绑定状态:</span>
            <span :class="getBindStatusClass(selectedStudent?.bind_status)" class="px-2 py-1 text-xs rounded-full">
              {{ getBindStatusText(selectedStudent?.bind_status) }}
            </span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-500">创建时间:</span>
            <span class="font-medium">{{ formatDate(selectedStudent?.created_at) }}</span>
          </div>
        </div>
        <div class="flex justify-end mt-6">
          <button @click="showDetailModal = false" class="btn-primary">关闭</button>
        </div>
      </div>
    </div>

    <div v-if="showGrowthModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl p-6 w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-bold">成长记录 - {{ selectedStudent?.name_in_class }}</h2>
          <button @click="showGrowthModal = false" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="flex-1 overflow-y-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">变化值</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">原因</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">操作人</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">时间</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="record in growthRecords" :key="record.id">
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                  <span :class="record.change_value >= 0 ? 'text-green-600' : 'text-red-600'" class="font-medium">
                    {{ record.change_value >= 0 ? '+' : '' }}{{ record.change_value }}
                  </span>
                </td>
                <td class="px-6 py-4 text-sm text-gray-500">{{ record.reason }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ record.operator_name }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ formatDate(record.created_at) }}</td>
              </tr>
            </tbody>
          </table>
          <div v-if="growthRecords.length === 0" class="text-center py-8">
            <p class="text-gray-500">暂无成长记录</p>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showLogsModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl p-6 w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-bold">操作日志 - {{ selectedStudent?.name_in_class }}</h2>
          <button @click="showLogsModal = false" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="flex-1 overflow-y-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">操作类型</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">描述</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">操作人</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">时间</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="log in studentLogs" :key="log.id">
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ log.operation_type }}</td>
                <td class="px-6 py-4 text-sm text-gray-500">{{ log.description }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ log.operator_name }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ formatDate(log.created_at) }}</td>
              </tr>
            </tbody>
          </table>
          <div v-if="studentLogs.length === 0" class="text-center py-8">
            <p class="text-gray-500">暂无操作日志</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import request from '@/api/request';
import { onMounted, ref } from 'vue';

interface Student {
  id: number;
  name: string;
  name_in_class: string;
  class_id: number;
  class_name: string;
  bind_status: string;
  is_deleted: boolean;
  created_at: string;
}

interface ClassInfo {
  id: number;
  class_name: string;
}

interface GrowthRecord {
  id: number;
  change_value: number;
  reason: string;
  operator_name: string;
  created_at: string;
}

interface StudentLog {
  id: number;
  operation_type: string;
  description: string;
  operator_name: string;
  created_at: string;
}

const students = ref<Student[]>([]);
const classes = ref<ClassInfo[]>([]);
const growthRecords = ref<GrowthRecord[]>([]);
const studentLogs = ref<StudentLog[]>([]);
const searchKeyword = ref('');
const selectedClass = ref('');
const selectedBindStatus = ref('');
const selectedIsDeleted = ref('');
const showDetailModal = ref(false);
const showGrowthModal = ref(false);
const showLogsModal = ref(false);
const selectedStudent = ref<Student | null>(null);

const fetchStudents = async () => {
  try {
    const params: Record<string, any> = {};
    if (selectedClass.value) params.class_id = selectedClass.value;
    if (selectedBindStatus.value) params.bind_status = selectedBindStatus.value;
    if (selectedIsDeleted.value) params.is_deleted = selectedIsDeleted.value === 'true';
    if (searchKeyword.value) params.keyword = searchKeyword.value;
    const data = (await request.get('/api/v1/admin/students', { params })) as { items: Student[] };
    students.value = data.items || [];
  } catch (error) {
    console.error('获取学员列表失败:', error);
  }
};

const fetchClasses = async () => {
  try {
    const data = (await request.get('/api/v1/admin/classes')) as { items: ClassInfo[] };
    classes.value = data.items || [];
  } catch (error) {
    console.error('获取班级列表失败:', error);
  }
};

const handleSearch = () => {
  fetchStudents();
};

const viewDetail = async (student: Student) => {
  selectedStudent.value = student;
  showDetailModal.value = true;
};

const viewGrowth = async (student: Student) => {
  selectedStudent.value = student;
  try {
    const data = (await request.get(`/api/v1/admin/students/${student.id}/growth-records`)) as { items: GrowthRecord[] };
    growthRecords.value = data.items || [];
    showGrowthModal.value = true;
  } catch (error) {
    console.error('获取成长记录失败:', error);
  }
};

const viewLogs = async (student: Student) => {
  selectedStudent.value = student;
  try {
    const data = (await request.get(`/api/v1/admin/students/${student.id}/logs`)) as { items: StudentLog[] };
    studentLogs.value = data.items || [];
    showLogsModal.value = true;
  } catch (error) {
    console.error('获取操作日志失败:', error);
  }
};

const unbindStudent = async (student: Student) => {
  if (!confirm(`确定要解绑学员"${student.name_in_class}"吗？`)) return;
  try {
    await request.post(`/api/v1/admin/students/${student.id}/unbind`);
    fetchStudents();
  } catch (error) {
    console.error('解绑学员失败:', error);
  }
};

const deleteStudent = async (student: Student) => {
  if (!confirm(`确定要删除学员"${student.name_in_class}"吗？此操作不可恢复。`)) return;
  try {
    await request.delete(`/api/v1/admin/students/${student.id}`);
    fetchStudents();
  } catch (error) {
    console.error('删除学员失败:', error);
  }
};

const getBindStatusClass = (status: string | undefined): string => {
  const classes: Record<string, string> = {
    approved: 'bg-green-100 text-green-800',
    pending: 'bg-yellow-100 text-yellow-800',
    rejected: 'bg-red-100 text-red-800',
  };
  return classes[status || ''] || 'bg-gray-100 text-gray-800';
};

const getBindStatusText = (status: string | undefined): string => {
  const statusMap: Record<string, string> = {
    approved: '已绑定',
    pending: '待审核',
    rejected: '已拒绝',
  };
  return statusMap[status || ''] || '未绑定';
};

const formatDate = (date: string | undefined) => {
  if (!date) return '-';
  return new Date(date).toLocaleString('zh-CN');
};

onMounted(() => {
  fetchStudents();
  fetchClasses();
});
</script>
