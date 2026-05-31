<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-900">历史成员</h1>
    </div>

    <!-- 搜索 -->
    <div class="bg-white rounded-lg shadow p-4">
      <div class="flex items-center gap-4">
        <div class="w-48 min-w-[150px]">
          <input
            v-model="searchKeyword"
            type="text"
            class="input w-full"
            placeholder="搜索成员姓名"
            @input="handleSearch"
          />
        </div>
      </div>
    </div>

    <!-- 历史成员列表 -->
    <div class="bg-white rounded-lg shadow p-4">
      <div class="overflow-x-auto">
        <table class="min-w-full">
          <thead>
            <tr class="bg-gray-100">
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                学号
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                姓名
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                组织
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                操作时间
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                操作原因
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                操作人
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                操作
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="student in historyStudents" :key="student.id">
              <td class="px-6 py-4 whitespace-nowrap">
                {{ student.student_no_in_class }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                {{ student.name_in_class }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                {{ student.class_name }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                {{ formatDate(student.deleted_at) }}
              </td>
              <td class="px-6 py-4">
                {{ student.remove_reason || '未说明' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                {{ student.operator_name || '未知' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <button
                  @click="viewStudentDetail(student)"
                  class="text-primary-600 hover:text-primary-700 mr-3"
                >
                  查看详情
                </button>
                <button
                  @click="restoreStudent(student)"
                  class="text-green-600 hover:text-green-700"
                >
                  恢复
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 分页 -->
      <div class="flex justify-between items-center mt-4">
        <div class="text-sm text-gray-500">
          共 {{ historyStudentsTotal }} 条记录
        </div>
        <div class="flex space-x-2">
          <button
            @click="skip > 0 && (skip -= 20) && fetchHistoryStudents()"
            :disabled="skip === 0"
            class="btn-secondary"
          >
            上一页
          </button>
          <button
            @click="
              () => {
                skip += 20;
                fetchHistoryStudents();
              }
            "
            :disabled="historyStudents.length < 20"
            class="btn-secondary"
          >
            下一页
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import request from '@/api/request';
import { useUserStore } from '@/stores/user';
import { ref, defineEmits } from 'vue';

interface Student {
  id: number;
  name_in_class: string;
  student_no_in_class: string;
  class_name: string;
  school_name: string;
  session: string;
  class_id: number;
  available_score: number;
  is_approved: boolean;
  is_registered: boolean;
  bind_status_text: string;
  tags?: any[];
  deleted_at: string;
  remove_reason: string;
  operator_name: string;
}

const props = defineProps<{
  viewStudentDetail: (student: Student) => void;
}>();

const emit = defineEmits<{
  'refresh-students': [];
}>();

// 历史成员相关状态
const historyStudents = ref<Student[]>([]);
const historyStudentsTotal = ref(0);
const skip = ref(0);
const searchKeyword = ref('');

// 用户存储
const userStore = useUserStore();

// 格式化日期
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN');
};

// 获取历史成员
const fetchHistoryStudents = async () => {
  try {
    console.log('开始获取历史成员数据');

    // 直接尝试获取历史成员数据，不依赖用户登录状态
    // 因为request拦截器会自动处理token
    const params = new URLSearchParams();
    if (searchKeyword.value) {
      params.append('keyword', searchKeyword.value);
      console.log('搜索关键词:', searchKeyword.value);
    }
    params.append('skip', skip.value.toString());
    params.append('limit', '20');
    console.log('请求参数:', params.toString());

    const url = `/v1/students/history-students?${params.toString()}`;
    console.log('发送请求:', url);
    const data = await request.get<any>(url);
    console.log('获取到的历史成员数据:', data);

    // 检查响应数据格式
    if (data && typeof data === 'object') {
      if (Array.isArray(data)) {
        // 响应是数组
        historyStudents.value = data;
        historyStudentsTotal.value = data.length;
        console.log('响应是数组，直接使用');
      } else if (data.items && Array.isArray(data.items)) {
        // 响应是带items的对象
        historyStudents.value = data.items;
        historyStudentsTotal.value = data.total || 0;
        console.log('响应是带items的对象，使用items字段');
      } else {
        // 响应格式不符合预期
        console.error('响应格式不符合预期:', data);
        historyStudents.value = [];
        historyStudentsTotal.value = 0;
      }
    } else {
      // 响应不是对象
      console.error('响应不是对象:', data);
      historyStudents.value = [];
      historyStudentsTotal.value = 0;
    }

    console.log('处理后的历史成员数据:', historyStudents.value);
    console.log('历史成员总数:', historyStudentsTotal.value);
  } catch (error) {
    console.error('获取历史成员失败:', error);
    // 打印更详细的错误信息
    if (error instanceof Error) {
      console.error('错误消息:', error.message);
      console.error('错误堆栈:', error.stack);
    } else {
      console.error('错误对象:', error);
    }
    historyStudents.value = [];
    historyStudentsTotal.value = 0;
  }
};

// 处理历史成员搜索
const handleSearch = () => {
  skip.value = 0;
  fetchHistoryStudents();
};

// 恢复成员
const restoreStudent = async (student: Student) => {
  if (confirm(`确定要恢复${student.name_in_class}吗？`)) {
    try {
      const response = await request.post(`/v1/students/restore/${student.id}`);
      // 刷新历史成员列表
      fetchHistoryStudents();
      // 通知父组件刷新成员列表
      emit('refresh-students');
      alert('恢复成功');
    } catch (error) {
      console.error('恢复成员失败:', error);
      alert('恢复失败，请稍后重试');
    }
  }
};

// 初始加载
fetchHistoryStudents();

// 暴露方法
defineExpose({
  fetchHistoryStudents,
});
</script>
