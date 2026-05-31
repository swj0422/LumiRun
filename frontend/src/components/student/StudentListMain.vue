<template>
  <div class="space-y-6">
    <!-- 页签切换 -->
    <div class="border-b border-gray-200">
      <nav class="flex -mb-px space-x-8">
        <button
          @click="activeTab = 'students'"
          :class="{
            'py-4 px-1 border-b-2 font-medium text-sm': true,
            'border-primary-500 text-primary-600': activeTab === 'students',
            'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300':
              activeTab !== 'students',
          }"
        >
          成员列表
        </button>
        <button
          @click="
            () => {
              activeTab = 'logs';
              fetchStudentOperationLogs();
            }
          "
          :class="{
            'py-4 px-1 border-b-2 font-medium text-sm': true,
            'border-primary-500 text-primary-600': activeTab === 'logs',
            'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300':
              activeTab !== 'logs',
          }"
        >
          成员日志
        </button>
      </nav>
    </div>

    <!-- 成员列表页签 -->
    <div v-show="activeTab === 'students'" class="space-y-6">
      <div class="flex justify-between items-center">
        <h1 class="text-2xl font-bold text-gray-900">成员列表</h1>
        <div class="flex space-x-2">
          <button @click="openAddModal" class="btn-primary">添加成员</button>
        </div>
      </div>

      <!-- 搜索和筛选 -->
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
          <select
            v-model="selectedSchool"
            class="input w-40"
            @change="fetchStudents"
          >
            <option value="">全部学校</option>
            <option v-for="school in schools" :key="school" :value="school">
              {{ school }}
            </option>
          </select>
          <select
            v-model="selectedSession"
            class="input w-32"
            @change="fetchStudents"
          >
            <option value="">全部级</option>
            <option v-for="session in sessions" :key="session" :value="session">
              {{ session }}级
            </option>
          </select>
          <select
            v-model="selectedClass"
            class="input w-48"
            @change="fetchStudents"
          >
            <option value="">全部组织</option>
            <option
              v-for="cls in classes"
              :key="cls.id"
              :value="cls.id"
            >
              {{ cls.class_name }}
            </option>
          </select>
          <select
            v-model="selectedStatus"
            class="input w-32"
            @change="fetchStudents"
          >
            <option value="">全部状态</option>
            <option value="active">正常</option>
            <option value="stopped">已停用</option>
          </select>
        </div>
      </div>

      <!-- 成员列表 -->
      <StudentTable
        :students="students"
        :total="totalStudents"
        :page-size="pageSize"
        :current-page="currentPage"
        :page-sizes="pageSizes"
        @page-change="handlePageChange"
        @size-change="handleSizeChange"
        @view-detail="viewStudentDetail"
        @open-growth-modal="openGrowthModal"
        @toggle-action-menu="toggleActionMenu"
        @stop-student="handleStopStudent"
        @activate-student="handleActivateStudent"
        @unbind-student="handleUnbindStudent"
        @delete-student="handleDeleteStudent"
        :active-action-menu="activeActionMenu"
      />
    </div>

    <!-- 成员日志页签 -->
    <div v-show="activeTab === 'logs'" class="space-y-6">
      <h1 class="text-2xl font-bold text-gray-900">成员日志</h1>
      <StudentOperationLogs
        :logs="operationLogs"
        :total="operationLogTotal"
        :skip="operationLogSkip"
        :search-keyword="operationLogSearchKeyword"
        :selected-operation-type="selectedOperationType"
        :start-date="operationLogStartDate"
        :end-date="operationLogEndDate"
        @fetch-logs="fetchStudentOperationLogs"
        @view-detail="viewOperationLogDetail"
      />
    </div>

    <!-- 成员详情弹窗 -->
    <StudentForm
      v-if="showDetailModal"
      ref="studentFormRef"
      :student="selectedStudentDetail"
      @close="closeDetailModal"
      @save="saveStudentDetail"
    />

    <!-- 成长值记录弹窗 -->
    <div
      v-if="showGrowthModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 class="text-lg font-bold mb-4">成长值记录</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1"
              >成员</label
            >
            <div class="text-gray-700">{{ selectedStudent?.name_in_class }}</div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1"
              >成长值变动</label
            >
            <input
              v-model.number="growthForm.score"
              type="number"
              class="input w-full"
              placeholder="请输入成长值变动"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1"
              >变动原因</label
            >
            <textarea
              v-model="growthForm.reason"
              class="input w-full"
              rows="3"
              placeholder="请输入变动原因"
            ></textarea>
          </div>
          <div class="flex justify-end space-x-3">
            <button
              @click="
                showGrowthModal = false;
                growthForm.score = 0;
                growthForm.reason = '';
              "
              class="btn-secondary"
            >
              取消
            </button>
            <button
              @click="addGrowthRecord"
              class="btn-primary"
              :disabled="!growthForm.reason"
            >
              确定
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 成员操作日志详情弹窗 -->
    <div
      v-if="showOperationLogDetailModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg p-6 w-full max-w-2xl">
        <h3 class="text-lg font-bold mb-4">操作日志详情</h3>
        <div class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1"
                >操作人</label
              >
              <div class="text-gray-700">
                {{ selectedOperationLog?.operator_name }}
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1"
                >操作时间</label
              >
              <div class="text-gray-700">
                {{ selectedOperationLog?.created_at }}
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1"
                >操作类型</label
              >
              <div class="text-gray-700">
                {{ selectedOperationLog?.operation_type }}
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1"
                >IP地址</label
              >
              <div class="text-gray-700">
                {{ selectedOperationLog?.ip_address }}
              </div>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1"
              >操作内容</label
            >
            <div class="text-gray-700">
              {{ selectedOperationLog?.operation_content }}
            </div>
          </div>
          <div v-if="selectedOperationLog?.before_data">
            <label class="block text-sm font-medium text-gray-700 mb-1"
              >操作前数据</label
            >
            <pre class="bg-gray-100 p-3 rounded text-sm">{{
              formatOperationData(selectedOperationLog?.before_data)
            }}</pre>
          </div>
          <div v-if="selectedOperationLog?.after_data">
            <label class="block text-sm font-medium text-gray-700 mb-1"
              >操作后数据</label
            >
            <pre class="bg-gray-100 p-3 rounded text-sm">{{
              formatOperationData(selectedOperationLog?.after_data)
            }}</pre>
          </div>
          <div class="flex justify-end">
            <button
              @click="
                showOperationLogDetailModal = false;
                selectedOperationLog = null;
              "
              class="btn-secondary"
            >
              关闭
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 停用成员对话框 -->
    <div
      v-if="showStopDialog"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 class="text-lg font-bold mb-4">停用成员</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1"
              >停用原因 <span class="text-red-500">*</span></label
            >
            <textarea
              v-model="form.stopReason"
              class="input w-full"
              rows="3"
              placeholder="请输入停用原因"
            ></textarea>
          </div>
          <div class="flex justify-end space-x-3">
            <button
              @click="
                showStopDialog = false;
                form.stopReason = '';
              "
              class="btn-secondary"
            >
              取消
            </button>
            <button
              @click="stopStudent(selectedStudentDetail)"
              class="btn-danger"
              :disabled="!form.stopReason"
            >
              确定停用
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 启用成员对话框 -->
    <div
      v-if="showActivateDialog"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 class="text-lg font-bold mb-4">启用成员</h3>
        <div class="space-y-4">
          <div>
            <p class="text-gray-700">确定要启用此成员吗？</p>
          </div>
          <div class="flex justify-end space-x-3">
            <button
              @click="
                showActivateDialog = false;
              "
              class="btn-secondary"
            >
              取消
            </button>
            <button
              @click="activateStudent(selectedStudentDetail)"
              class="btn-primary"
            >
              确定启用
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 解绑成员对话框 -->
    <div
      v-if="showUnbindDialog"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 class="text-lg font-bold mb-4">解绑成员</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1"
              >解绑原因 <span class="text-red-500">*</span></label
            >
            <textarea
              v-model="form.unbindReason"
              class="input w-full"
              rows="3"
              placeholder="请输入解绑原因"
            ></textarea>
          </div>
          <div class="flex justify-end space-x-3">
            <button
              @click="
                showUnbindDialog = false;
                form.unbindReason = '';
              "
              class="btn-secondary"
            >
              取消
            </button>
            <button
              @click="unbindStudent(selectedStudentDetail)"
              class="btn-danger"
              :disabled="!form.unbindReason"
            >
              确定解绑
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 删除成员对话框 -->
    <div
      v-if="showDeleteDialog"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 class="text-lg font-bold mb-4">删除成员</h3>
        <div class="space-y-4">
          <div>
            <p class="text-gray-700 mb-4">确定要删除此成员吗？删除后成员将移出本班，学号释放可重新使用。</p>
            <label class="block text-sm font-medium text-gray-700 mb-1"
              >删除原因 <span class="text-red-500">*</span></label
            >
            <textarea
              v-model="form.deleteReason"
              class="input w-full"
              rows="3"
              placeholder="请输入删除原因"
            ></textarea>
          </div>
          <div class="flex justify-end space-x-3">
            <button
              @click="
                showDeleteDialog = false;
                form.deleteReason = '';
              "
              class="btn-secondary"
            >
              取消
            </button>
            <button
              @click="deleteStudent(selectedStudentDetail)"
              class="btn-danger"
              :disabled="!form.deleteReason"
            >
              确定删除
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加成员弹窗 -->
    <div
      v-if="showAddModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 class="text-lg font-bold mb-4">添加成员</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1"
              >选择组织 <span class="text-red-500">*</span></label
            >
            <select
              v-model="form.class_id"
              class="input w-full"
            >
              <option value="">请选择组织</option>
              <option
                v-for="cls in classes"
                :key="cls.id"
                :value="cls.id"
              >
                {{ cls.school_name || '' }} {{ cls.session || '' }}级 {{ cls.class_name }}班
              </option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1"
              >学号 <span class="text-red-500">*</span></label
            >
            <input
              v-model="form.student_no"
              type="text"
              class="input w-full"
              placeholder="请输入学号"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1"
              >姓名 <span class="text-red-500">*</span></label
            >
            <input
              v-model="form.real_name"
              type="text"
              class="input w-full"
              placeholder="请输入成员姓名"
            />
          </div>
          <div class="flex justify-end space-x-3">
            <button
              @click="
                showAddModal = false;
                form.class_id = '';
                form.student_no = '';
                form.real_name = '';
              "
              class="btn-secondary"
            >
              取消
            </button>
            <button
              @click="addStudent"
              class="btn-primary"
              :disabled="!form.class_id || !form.student_no || !form.real_name"
            >
              确定添加
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useUserStore } from '@/stores/user';
import request from '@/api/request';
import StudentTable from './StudentTable.vue';
import StudentOperationLogs from './StudentOperationLogs.vue';
import StudentForm from './StudentForm.vue';

// 成员表单组件引用
const studentFormRef = ref<InstanceType<typeof StudentForm> | null>(null);

interface Student {
  id: number;
  name_in_class: string;
  student_no_in_class: string;
  class_name: string;
  school_name: string;
  session: string;
  class_id: number;
  available_score: number;
  total_score: number;
  is_registered: boolean;
  bind_status: string;
  bind_status_text: string;
  is_active: boolean;
  tags?: any[];
}

interface ClassInfo {
  id: number;
  class_name: string;
  school_name?: string;
  session?: string;
}

const students = ref<Student[]>([]);
const classes = ref<ClassInfo[]>([]);
const searchKeyword = ref('');
const selectedSchool = ref('');
const selectedSession = ref('');
const selectedClass = ref('');
const selectedStatus = ref('');
const showGrowthModal = ref(false);
const selectedStudent = ref<Student | null>(null);
const growthForm = ref({
  score: 0,
  reason: '',
});

// 添加成员和批量导入相关状态
const showAddModal = ref(false);
const editingStudent = ref<any>(null);
const addMode = ref('single'); // 'single' 或 'batch'
const form = ref({
  class_id: '',
  student_no: '',
  real_name: '',
  stopReason: '',
  unbindReason: '',
  deleteReason: '',
});
const batchForm = ref({
  class_id: '',
});
const fileInput = ref<HTMLInputElement | null>(null);
const uploadedFile = ref<File | null>(null);
const uploadedFileName = ref('');

// 成员详情弹窗相关状态
const showDetailModal = ref(false);
const selectedStudentDetail = ref<Student | null>(null);
const showStopDialog = ref(false);
const showActivateDialog = ref(false);
const showUnbindDialog = ref(false);
const showDeleteDialog = ref(false);
// 操作菜单状态
const activeActionMenu = ref<number | undefined>(undefined);
const studentNote = ref({
  learning_characteristics: '',
  personality_suggestions: '',
  performance_summary: '',
});

// 原始备注和标签，用于比较是否有变化
const originalStudentNote = ref({
  learning_characteristics: '',
  personality_suggestions: '',
  performance_summary: '',
});

// 成员标签相关状态
const studentTags = ref<any[]>([]);
const selectedTags = ref<number[]>([]);
const originalSelectedTags = ref<number[]>([]);
const availableStudentTags = ref<any[]>([]);

// 页签状态
const activeTab = ref('students');

// 成员日志相关状态
const studentLogs = ref<any[]>([]);
const logTotal = ref(0);
const logSkip = ref(0);
const logSearchKeyword = ref('');
const selectedLogModule = ref('');

// 成员操作日志相关状态
const operationLogs = ref<any[]>([]);
const operationLogTotal = ref(0);
const operationLogSkip = ref(0);
const operationLogSearchKeyword = ref('');
const selectedOperationType = ref('');
const operationLogStartDate = ref('');
const operationLogEndDate = ref('');
const showOperationLogDetailModal = ref(false);
const selectedOperationLog = ref<any>(null);

// 分页相关状态
const operationLogCurrentPage = ref(1);

// 分页相关状态
const pageSize = ref(20);
const pageSizes = ref([10, 20, 50, 100]);
const currentPage = ref(1);
const totalStudents = ref(0);

// 用户存储
const userStore = useUserStore();

// 计算唯一组织列表
const uniqueClasses = computed(() => {
  const classSet = new Set<string>();
  const unique: { class_name: string }[] = [];

  // 从 classes 中提取组织名称，确保没有成员的组织也能显示
  classes.value.forEach((cls) => {
    if (cls.class_name && !classSet.has(cls.class_name)) {
      classSet.add(cls.class_name);
      unique.push({ class_name: cls.class_name });
    }
  });

  return unique;
});

// 计算学校列表
const schools = computed(() => {
  const schoolSet = new Set<string>();
  classes.value.forEach((cls) => {
    if (cls.school_name) {
      schoolSet.add(cls.school_name);
    }
  });
  return Array.from(schoolSet);
});

// 计算级列表
const sessions = computed(() => {
  const sessionSet = new Set<string>();
  classes.value.forEach((cls) => {
    if (cls.session) {
      sessionSet.add(cls.session);
    }
  });
  return Array.from(sessionSet).sort().reverse();
});

// 获取组织列表
const fetchClasses = async () => {
  try {
    console.log('开始获取组织列表');
    const response = await request.get('/api/v1/classes/');
    console.log('组织列表响应:', response);
    if (response && response.items) {
      // 响应是对象，使用items字段
      classes.value = response.items;
    } else if (Array.isArray(response)) {
      // 响应是数组，直接使用
      classes.value = response;
    } else if (response.code === 200 && response.data) {
      // 响应是ApiResponse格式，使用data字段
      classes.value = response.data;
    } else {
      // 其他情况，设置为空数组
      classes.value = [];
    }
    console.log('组织数据更新成功:', classes.value);
  } catch (error) {
    console.error('获取组织列表失败:', error);
    // 出错时，设置为空数组
    classes.value = [];
  }
};

// 获取成员列表
const fetchStudents = async () => {
    try {
      console.log('开始获取成员列表');
      // 构建参数，只包含非空值
      const params: any = {
        skip: (currentPage.value - 1) * pageSize.value,
        limit: pageSize.value,
        keyword: searchKeyword.value,
      };
      
      // 只有当school_name不为空时才添加到参数中
      if (selectedSchool.value) {
        params.school_name = selectedSchool.value;
      }
      
      // 只有当status不为空时才添加到参数中
      if (selectedStatus.value) {
        params.status = selectedStatus.value;
      }
      
      // 只有当class_id不为空且是有效数字时才添加到参数中
      if (selectedClass.value && !isNaN(Number(selectedClass.value))) {
        params.class_id = Number(selectedClass.value);
      }
      
      // 只有当session不为空时才添加到参数中
      if (selectedSession.value) {
        params.session = selectedSession.value;
      }
      
      console.log('成员列表请求参数:', params);
      console.log('请求地址:', '/api/v1/students/teacher-students');
      const response = await request.get('/api/v1/students/teacher-students', {
        params,
      });
      console.log('成员列表响应:', response);
      console.log('响应类型:', typeof response);
      console.log('响应是否是对象:', typeof response === 'object' && response !== null);
      console.log('响应是否包含items字段:', response && 'items' in response);
      // 检查响应格式
      if (response && 'items' in response) {
        // 响应是对象，使用items字段
        students.value = response.items;
        totalStudents.value = response.total || 0;
        console.log('成员数据更新成功（对象格式）:', students.value);
        console.log('成员数量:', students.value.length);
        console.log('总成员数:', totalStudents.value);
        // 检查第一个成员的结构
        if (students.value.length > 0) {
          console.log('第一个成员数据:', students.value[0]);
          console.log('第一个成员姓名字段:', students.value[0].name_in_class);
        }
      } else if (response && 'code' in response && response.code === 200 && 'data' in response) {
        // 响应是ApiResponse格式，使用data字段
        if (response.data && 'items' in response.data) {
          students.value = response.data.items;
          totalStudents.value = response.data.total || 0;
        } else {
          students.value = response.data;
          totalStudents.value = response.data.length || 0;
        }
        console.log('成员数据更新成功（ApiResponse格式）:', students.value);
        console.log('成员数量:', students.value.length);
        console.log('总成员数:', totalStudents.value);
      } else if (Array.isArray(response)) {
        // 响应是数组，直接使用
        students.value = response;
        totalStudents.value = response.length || 0;
        console.log('成员数据更新成功（数组格式）:', students.value);
        console.log('成员数量:', students.value.length);
        console.log('总成员数:', totalStudents.value);
      } else {
        console.error('响应格式不正确:', response);
        students.value = [];
        totalStudents.value = 0;
        console.log('成员数据设置为空数组');
      }
    } catch (error) {
      console.error('获取成员列表失败:', error);
      students.value = [];
      totalStudents.value = 0;
      console.log('成员数据设置为空数组');
    }
  };

// 搜索成员
const handleSearch = () => {
  currentPage.value = 1;
  fetchStudents();
};

// 格式化操作日志数据
const formatOperationData = (data: any) => {
  if (!data) return '';
  if (typeof data === 'string') {
    try {
      const parsed = JSON.parse(data);
      return JSON.stringify(parsed, null, 2);
    } catch {
      return data;
    }
  }
  return JSON.stringify(data, null, 2);
};

// 分页处理
const handlePageChange = (page: number) => {
  currentPage.value = page;
  fetchStudents();
};

const handleSizeChange = (size: number) => {
  pageSize.value = size;
  currentPage.value = 1;
  fetchStudents();
};

// 打开成长值记录弹窗
const openGrowthModal = (student: Student) => {
  selectedStudent.value = student;
  showGrowthModal.value = true;
};

// 添加成长值记录
const addGrowthRecord = async () => {
  if (!selectedStudent.value || !growthForm.value.reason) return;

  try {
    await request.post('/api/v1/growth/record', {
      student_name: selectedStudent.value.name_in_class,
      change_score: growthForm.value.score,
      reason: growthForm.value.reason,
    });
    showGrowthModal.value = false;
    growthForm.value.score = 0;
    growthForm.value.reason = '';
    fetchStudents();
  } catch (error) {
    console.error('添加成长值失败:', error);
  }
};

// 查看成员详情
const viewStudentDetail = (student: Student) => {
  selectedStudentDetail.value = student;
  showDetailModal.value = true;
};

// 关闭成员详情弹窗
const closeDetailModal = () => {
  showDetailModal.value = false;
  selectedStudentDetail.value = null;
  form.value.stopReason = '';
  form.value.unbindReason = '';
  form.value.deleteReason = '';
};

// 保存成员详情
const saveStudentDetail = async () => {
  console.log('开始保存成员详情');
  console.log('selectedStudentDetail:', selectedStudentDetail);
  if (!selectedStudentDetail.value || !selectedStudentDetail.value.id) {
    console.error('成员详情或ID不存在');
    return;
  }

  try {
    // 获取标签数据
    const selectedTags = studentFormRef.value?.getSelectedTags() || [];
    const originalSelectedTags = studentFormRef.value?.getOriginalSelectedTags() || [];
    console.log('选中的标签:', selectedTags);
    console.log('原始标签:', originalSelectedTags);
    
    // 检查标签是否有变化
    const tagsChanged = JSON.stringify(selectedTags.sort()) !== JSON.stringify(originalSelectedTags.sort());
    if (tagsChanged) {
      // 保存标签
      console.log('开始保存标签，成员ID:', selectedStudentDetail.value.id);
      const tagResponse = await request.post(`/api/v1/students/tags/${selectedStudentDetail.value.id}`, {
        tag_ids: selectedTags
      });
      console.log('保存标签成功，响应:', tagResponse);
    } else {
      console.log('标签未变化，跳过保存');
    }

    // 保存成员信息
    const formData = studentFormRef.value?.getForm() || {};
    const realName = (formData as any).real_name;
    // 只有当姓名实际改变时才调用更新接口
    if (realName && realName !== selectedStudentDetail.value.name_in_class) {
      await request.put(`/api/v1/students/${selectedStudentDetail.value.id}`, {
        real_name: realName
      });
    } else {
      console.log('姓名未变化，跳过保存');
    }

    // 保存成员备注
    const studentNote = studentFormRef.value?.getStudentNote() || {};
    const originalStudentNote = studentFormRef.value?.getOriginalStudentNote() || {};
    console.log('成员备注:', studentNote);
    console.log('原始备注:', originalStudentNote);

    // 构建备注数据，包含标签
    const noteData = {
      ...studentNote,
      tags: JSON.stringify(selectedTags)
    };
    console.log('备注数据（含标签）:', noteData);

    // 检查备注是否有变化（包括标签变化）
    const noteTagsChanged = JSON.stringify(selectedTags.sort()) !== JSON.stringify(originalSelectedTags.sort());
    const noteFieldsChanged = JSON.stringify(studentNote) !== JSON.stringify(originalStudentNote);
    if (noteTagsChanged || noteFieldsChanged) {
      console.log('开始保存备注，成员ID:', selectedStudentDetail.value.id);
      const noteResponse = await request.post(`/api/v1/students/note/${selectedStudentDetail.value.id}`, noteData);
      console.log('保存备注成功，响应:', noteResponse);
    } else {
      console.log('备注未变化，跳过保存');
    }

    closeDetailModal();
    fetchStudents();
    // 总是刷新日志列表，确保最新的变更显示
    fetchStudentOperationLogs();
    console.log('保存成员详情完成');
  } catch (error) {
    console.error('保存成员详情失败:', error);
    alert('保存失败，请稍后重试');
  }
};

// 切换操作菜单
const toggleActionMenu = (studentId: number) => {
  activeActionMenu.value =
    activeActionMenu.value === studentId ? undefined : studentId;
};

// 处理停用成员
const handleStopStudent = (student: Student) => {
  selectedStudentDetail.value = student;
  showStopDialog.value = true;
};

// 处理启用成员
const handleActivateStudent = (student: Student) => {
  selectedStudentDetail.value = student;
  showActivateDialog.value = true;
};

// 处理解绑成员
const handleUnbindStudent = (student: Student) => {
  selectedStudentDetail.value = student;
  showUnbindDialog.value = true;
};

// 处理删除成员
const handleDeleteStudent = (student: Student) => {
  selectedStudentDetail.value = student;
  showDeleteDialog.value = true;
};

// 停用成员
const stopStudent = async (student: Student | null) => {
  if (!student || !form.value.stopReason) return;

  try {
    await request.post(`/api/v1/students/stop/${student.id}`, {
      reason: form.value.stopReason,
    });
    showStopDialog.value = false;
    form.value.stopReason = '';
    fetchStudents();
  } catch (error) {
    console.error('停用成员失败:', error);
  }
};

// 启用成员
const activateStudent = async (student: Student | null) => {
  if (!student) return;

  try {
    await request.post(`/api/v1/students/activate/${student.id}`);
    showActivateDialog.value = false;
    fetchStudents();
  } catch (error) {
    console.error('启用成员失败:', error);
  }
};

// 解绑成员
const unbindStudent = async (student: Student | null) => {
  if (!student || !form.value.unbindReason) return;

  try {
    await request.post(`/api/v1/students/unbind/${student.id}`, {
      reason: form.value.unbindReason,
    });
    showUnbindDialog.value = false;
    form.value.unbindReason = '';
    fetchStudents();
  } catch (error) {
    console.error('解绑成员失败:', error);
  }
};

// 删除成员
const deleteStudent = async (student: Student | null) => {
  if (!student || !form.value.deleteReason) return;

  try {
    await request.post(`/api/v1/students/delete/${student.id}`, {
      reason: form.value.deleteReason,
    });
    showDeleteDialog.value = false;
    form.value.deleteReason = '';
    fetchStudents();
  } catch (error) {
    console.error('删除成员失败:', error);
  }
};

// 获取成员操作日志
const fetchStudentOperationLogs = async () => {
  try {
    console.log('开始获取成员操作日志');
    // 构建参数，只包含非空值
    const params: any = {
      skip: operationLogSkip.value,
      limit: 20,
      student_name: operationLogSearchKeyword.value,
      operation_type: selectedOperationType.value,
    };
    
    // 只有当日期不为空时才添加到参数中
    if (operationLogStartDate.value) {
      params.start_time = operationLogStartDate.value;
    }
    if (operationLogEndDate.value) {
      params.end_time = operationLogEndDate.value;
    }
    
    const response = await request.get('/api/v1/student-operation-logs/', {
      params,
    });
    console.log('成员操作日志响应:', response);
    // 检查响应数据格式
    if (Array.isArray(response)) {
      // 响应是数组，直接使用
      operationLogs.value = response;
      operationLogTotal.value = response.length;
      console.log('成员操作日志数据更新成功（数组格式）:', operationLogs.value);
    } else if (response && response.items) {
      // 响应是对象，使用items字段
      operationLogs.value = response.items;
      operationLogTotal.value = response.total || 0;
      console.log('成员操作日志数据更新成功（对象格式）:', operationLogs.value);
    } else {
      console.error('响应格式不正确:', response);
    }
  } catch (error) {
    console.error('获取成员操作日志失败:', error);
  }
};

// 查看操作日志详情
const viewOperationLogDetail = (log: any) => {
  selectedOperationLog.value = log;
  showOperationLogDetailModal.value = true;
};

// 打开添加成员弹窗
const openAddModal = () => {
  showAddModal.value = true;
};

// 添加成员
const addStudent = async () => {
  if (!form.value.class_id || !form.value.student_no || !form.value.real_name) return;

  try {
    await request.post('/api/v1/students/', {
      class_id: form.value.class_id,
      student_no: form.value.student_no,
      real_name: form.value.real_name,
    });
    showAddModal.value = false;
    form.value.class_id = '';
    form.value.student_no = '';
    form.value.real_name = '';
    fetchStudents();
  } catch (error) {
    console.error('添加成员失败:', error);
  }
};

// 初始化
onMounted(async () => {
  console.log('开始初始化数据');
  await fetchClasses();
  console.log('组织数据获取完成:', classes.value);
  console.log('组织数量:', classes.value.length);
  await fetchStudents();
  console.log('成员数据获取完成:', students.value);
  console.log('成员数量:', students.value.length);
  console.log('总成员数:', totalStudents.value);
  console.log('students 类型:', typeof students);
  console.log('students.value 类型:', typeof students.value);
  console.log('students.value 是否是数组:', Array.isArray(students.value));
});
</script>
