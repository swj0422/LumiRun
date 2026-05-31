<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-900">成员管理</h1>
      <div class="flex items-center space-x-4">
        <div class="relative">
          <select v-model="selectedClassId" class="input pr-8">
            <option value="">选择组织</option>
            <option v-for="classItem in classes" :key="classItem.id" :value="classItem.id">
              {{ classItem.school_name }} {{ classItem.session }}级 {{ classItem.class_name }}班
            </option>
          </select>
        </div>
      </div>
    </div>

    <!-- 成员列表 -->
    <div class="bg-white shadow rounded-lg p-6">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th
                scope="col"
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                序号
              </th>
              <th
                scope="col"
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                姓名
              </th>
              <th
                scope="col"
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                学号
              </th>
              <th
                scope="col"
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                状态
              </th>
              <th
                scope="col"
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                绑定时间
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="(student, index) in students" :key="student.id">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ index + 1 }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ student.name_in_class }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ student.student_no_in_class }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full"
                  :class="getBindStatusClass(student.bind_status)"
                >
                  {{ getBindStatusText(student.bind_status) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(student.created_at) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="students.length === 0" class="text-center py-8">
        <p class="text-gray-500">暂无成员数据</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import { getUserAssistantClasses } from '@/api/class';
import request from '@/api/request';

const route = useRoute();
const classes = ref<any[]>([]);
const students = ref<any[]>([]);
const selectedClassId = ref('');

// 从路由参数中获取组织ID
const initClassId = () => {
  const classId = route.query.class_id;
  if (classId) {
    selectedClassId.value = classId as string;
  }
};

// 获取授权组织列表
const fetchClasses = async () => {
  try {
    const data = await getUserAssistantClasses();
    classes.value = (data as any).items || [];
    // 如果没有选择组织，默认选择第一个
    if (!selectedClassId.value && classes.value.length > 0) {
      selectedClassId.value = classes.value[0].id;
    }
  } catch (error) {
    console.error('获取授权组织失败:', error);
    classes.value = [];
  }
};

// 获取组织成员列表
const fetchStudents = async () => {
  if (!selectedClassId.value) {
    students.value = [];
    return;
  }

  try {
    const data = await request.get(`/api/v1/classes/${selectedClassId.value}/students`);
    students.value = (data as any).items || [];
  } catch (error) {
    console.error('获取成员列表失败:', error);
    students.value = [];
  }
};

// 格式化日期
const formatDate = (dateString: string) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN');
};

// 获取绑定状态的样式
const getBindStatusClass = (status: string) => {
  switch (status) {
    case 'approved':
      return 'bg-green-100 text-green-800';
    case 'pending':
      return 'bg-yellow-100 text-yellow-800';
    case 'rejected':
      return 'bg-red-100 text-red-800';
    case 'none':
      return 'bg-gray-100 text-gray-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

// 获取绑定状态的文本
const getBindStatusText = (status: string) => {
  switch (status) {
    case 'approved':
      return '已绑定';
    case 'pending':
      return '待审核';
    case 'rejected':
      return '已拒绝';
    case 'none':
      return '未绑定';
    default:
      return '未知';
  }
};

// 监听组织选择变化
watch(selectedClassId, () => {
  fetchStudents();
});

onMounted(async () => {
  initClassId();
  await fetchClasses();
  await fetchStudents();
});
</script>
