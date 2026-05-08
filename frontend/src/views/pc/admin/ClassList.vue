<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-900">班级管理</h1>
    </div>

    <div class="bg-white rounded-lg shadow p-4">
      <div class="flex flex-wrap gap-4">
        <input
          v-model="searchKeyword"
          type="text"
          class="input flex-1 min-w-[200px]"
          placeholder="搜索学校或班级名称"
          @input="handleSearch"
        />
        <select v-model="selectedStatus" class="input w-32" @change="fetchClasses">
          <option value="">全部状态</option>
          <option value="true">开放</option>
          <option value="false">关闭</option>
        </select>
      </div>
    </div>

    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">学校</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">届别</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">班级名称</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">导师</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">学员数</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">创建时间</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="cls in classes" :key="cls.id">
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ cls.school_name }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ cls.session }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ cls.class_name }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ cls.teacher_name }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ cls.student_count }}</td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="cls.status ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'" class="px-2 py-1 text-xs rounded-full">
                {{ cls.status ? '开放' : '关闭' }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ formatDate(cls.created_at) }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
              <button @click="viewStudents(cls)" class="text-blue-600 hover:text-blue-700 mr-2">学员</button>
              <button @click="viewGrowth(cls)" class="text-green-600 hover:text-green-700 mr-2">成长记录</button>
              <button
                v-if="cls.status"
                @click="closeClass(cls.id)"
                class="text-yellow-600 hover:text-yellow-700 mr-2"
              >
                关闭
              </button>
              <button v-else @click="openClass(cls.id)" class="text-green-600 hover:text-green-700 mr-2">开放</button>
              <button @click="deleteClass(cls)" class="text-red-600 hover:text-red-700">删除</button>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="classes.length === 0" class="text-center py-12">
        <p class="text-gray-500">暂无班级数据</p>
      </div>
    </div>

    <div v-if="showStudentsModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl p-6 w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-bold">班级学员 - {{ selectedClass?.class_name }}</h2>
          <button @click="showStudentsModal = false" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="flex-1 overflow-y-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">姓名</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">班级昵称</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">绑定状态</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">创建时间</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="student in students" :key="student.id">
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ student.name }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ student.name_in_class }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                  <span :class="student.bind_status === 'approved' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'" class="px-2 py-1 text-xs rounded-full">
                    {{ getBindStatusText(student.bind_status) }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ formatDate(student.created_at) }}</td>
              </tr>
            </tbody>
          </table>
          <div v-if="students.length === 0" class="text-center py-8">
            <p class="text-gray-500">暂无学员数据</p>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showGrowthModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl p-6 w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-bold">成长记录 - {{ selectedClass?.class_name }}</h2>
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
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">学员</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">变化值</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">原因</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">操作人</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">时间</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="record in growthRecords" :key="record.id">
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ record.student_name }}</td>
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
  </div>
</template>

<script setup lang="ts">
import request from '@/api/request';
import { onMounted, ref } from 'vue';

interface ClassInfo {
  id: number;
  school_name: string;
  session: string;
  class_name: string;
  teacher_name: string;
  student_count: number;
  status: boolean;
  created_at: string;
}

interface Student {
  id: number;
  name: string;
  name_in_class: string;
  bind_status: string;
  created_at: string;
}

interface GrowthRecord {
  id: number;
  student_name: string;
  change_value: number;
  reason: string;
  operator_name: string;
  created_at: string;
}

const classes = ref<ClassInfo[]>([]);
const students = ref<Student[]>([]);
const growthRecords = ref<GrowthRecord[]>([]);
const searchKeyword = ref('');
const selectedStatus = ref('');
const showStudentsModal = ref(false);
const showGrowthModal = ref(false);
const selectedClass = ref<ClassInfo | null>(null);

const fetchClasses = async () => {
  try {
    const params: Record<string, any> = {};
    if (selectedStatus.value) params.status = selectedStatus.value === 'true';
    if (searchKeyword.value) params.keyword = searchKeyword.value;
    const data = (await request.get('/api/v1/admin/classes', { params })) as { items: ClassInfo[] };
    classes.value = data.items || [];
  } catch (error) {
    console.error('获取班级列表失败:', error);
  }
};

const handleSearch = () => {
  fetchClasses();
};

const viewStudents = async (cls: ClassInfo) => {
  selectedClass.value = cls;
  try {
    const data = (await request.get(`/api/v1/admin/classes/${cls.id}/students`)) as { items: Student[] };
    students.value = data.items || [];
    showStudentsModal.value = true;
  } catch (error) {
    console.error('获取学员列表失败:', error);
  }
};

const viewGrowth = async (cls: ClassInfo) => {
  selectedClass.value = cls;
  try {
    const data = (await request.get(`/api/v1/admin/classes/${cls.id}/growth-records`)) as { items: GrowthRecord[] };
    growthRecords.value = data.items || [];
    showGrowthModal.value = true;
  } catch (error) {
    console.error('获取成长记录失败:', error);
  }
};

const closeClass = async (classId: number) => {
  if (!confirm('确定要关闭该班级吗？')) return;
  try {
    await request.put(`/api/v1/admin/classes/${classId}/status`, { status: false });
    fetchClasses();
  } catch (error) {
    console.error('关闭班级失败:', error);
  }
};

const openClass = async (classId: number) => {
  try {
    await request.put(`/api/v1/admin/classes/${classId}/status`, { status: true });
    fetchClasses();
  } catch (error) {
    console.error('开放班级失败:', error);
  }
};

const deleteClass = async (cls: ClassInfo) => {
  if (!confirm(`确定要删除班级"${cls.class_name}"吗？此操作不可恢复。`)) return;
  try {
    await request.delete(`/api/v1/admin/classes/${cls.id}`);
    fetchClasses();
  } catch (error) {
    console.error('删除班级失败:', error);
  }
};

const getBindStatusText = (status: string): string => {
  const statusMap: Record<string, string> = {
    approved: '已绑定',
    pending: '待审核',
    rejected: '已拒绝',
  };
  return statusMap[status] || status;
};

const formatDate = (date: string) => {
  return new Date(date).toLocaleString('zh-CN');
};

onMounted(() => {
  fetchClasses();
});
</script>
