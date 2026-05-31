<template>
  <div class="space-y-4 p-4">
    <div class="flex justify-between items-center">
      <h1 class="text-xl font-bold text-gray-900">组织详情</h1>
      <button
        @click="router.push('/teacher/classes')"
        class="btn-secondary px-3 py-1 text-sm"
      >
        返回
      </button>
    </div>

    <!-- 组织信息 -->
    <div class="bg-white rounded-lg shadow p-4">
      <div class="space-y-3">
        <!-- 状态标签 -->
        <div class="flex justify-end">
          <span
            :class="
              classInfo?.status
                ? 'bg-green-100 text-green-800'
                : 'bg-gray-100 text-gray-800'
            "
            class="px-2 py-1 text-xs rounded-full"
          >
            {{ classInfo?.status ? '正常' : '已关闭' }}
          </span>
        </div>

        <!-- 组织基本信息 -->
        <div>
          <h2 class="text-lg font-semibold text-gray-800">
            {{ classInfo?.session }}级{{ classInfo?.class_name }}班
          </h2>
          <p class="text-sm text-gray-500 mt-1">{{ classInfo?.school_name }}</p>
        </div>

        <!-- 组织描述 -->
        <div class="mt-3">
          <div class="bg-gray-50 p-3 rounded-lg border border-gray-100">
            <p class="text-sm text-gray-700">
              {{ classInfo?.description || '暂无简介' }}
            </p>
          </div>
        </div>

        <!-- 二维码 -->
        <div class="flex flex-col items-center pt-3">
          <div class="w-48 h-48 bg-gray-100 flex items-center justify-center">
            <canvas ref="qrCanvas" class="max-w-full max-h-full" />
            <div v-if="!classInfo" class="text-gray-500 text-sm">
              二维码生成中...
            </div>
          </div>
          <p class="text-xs text-gray-500 mt-2">成员扫码绑定组织</p>
          <!-- 学生绑定组织信息 -->
          <div class="mt-4 p-3 bg-gray-50 rounded-lg border border-gray-100 w-full max-w-sm">
            <h3 class="text-sm font-semibold text-gray-700 mb-2">学生绑定组织</h3>
            <p class="text-xs text-gray-500 mb-2">如果学生无法扫码，可以手动输入以下信息：</p>
            <div class="space-y-1 text-xs text-gray-600">
              <p>1. 打开成员端首页</p>
              <p>2. 点击"手动输入"按钮</p>
              <p>3. 输入组织二维码内容：<span class="font-mono">{{ classInfo?.qr_url }}</span></p>
              <p>4. 输入老师提供的姓名和学号</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 组织助理 -->
    <div class="bg-white rounded-lg shadow p-4">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-lg font-semibold text-gray-800">组织助理</h2>
        <button
          @click="showAddAssistantModal = true"
          class="btn-primary px-3 py-1 text-sm"
        >
          添加助理
        </button>
      </div>

      <!-- 助理列表 -->
      <div v-if="assistants.length > 0" class="space-y-3">
        <div
          v-for="assistant in assistants"
          :key="assistant.id"
          class="flex justify-between items-center p-3 border border-gray-200 rounded-lg"
        >
          <div>
            <p class="font-medium text-gray-900">{{ assistant.assistant_name }}</p>
            <p class="text-sm text-gray-500">{{ assistant.assistant_email }}</p>
          </div>
          <button
            @click="removeAssistant(assistant.assistant_id)"
            class="text-red-600 hover:text-red-800 text-sm"
          >
            移除
          </button>
        </div>
      </div>
      <div v-else class="text-center py-6 text-gray-500">
        暂无组织助理
      </div>
    </div>

    <!-- 添加助理弹窗 -->
    <div v-if="showAddAssistantModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-lg p-6 w-full max-w-md">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">添加组织助理</h3>

        <div class="space-y-4">
          <!-- 授权方式选择 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">授权方式</label>
            <div class="space-y-2">
              <label class="flex items-center">
                <input
                  type="radio"
                  v-model="addAssistantMode"
                  value="student"
                  class="mr-2"
                />
                <span>从本班成员列表选择</span>
              </label>
              <label class="flex items-center">
                <input
                  type="radio"
                  v-model="addAssistantMode"
                  value="email"
                  class="mr-2"
                />
                <span>输入系统已注册用户的邮箱</span>
              </label>
            </div>
          </div>

          <!-- 从成员列表选择 -->
          <div v-if="addAssistantMode === 'student'">
            <label class="block text-sm font-medium text-gray-700 mb-2">选择成员</label>
            <select
              v-model="selectedStudentId"
              class="w-full border border-gray-300 rounded-md px-3 py-2"
            >
              <option value="">请选择成员</option>
              <option
                v-for="student in classStudents"
                :key="student.id"
                :value="student.id"
              >
                {{ student.real_name }}
              </option>
            </select>
          </div>

          <!-- 输入邮箱 -->
          <div v-else>
            <label class="block text-sm font-medium text-gray-700 mb-2">用户邮箱</label>
            <input
              type="email"
              v-model="assistantEmail"
              placeholder="请输入系统已注册用户的邮箱"
              class="w-full border border-gray-300 rounded-md px-3 py-2"
            />
          </div>

          <div class="flex justify-end space-x-3">
            <button
              @click="showAddAssistantModal = false"
              class="btn-secondary px-4 py-2"
            >
              取消
            </button>
            <button
              @click="addAssistant"
              class="btn-primary px-4 py-2"
            >
              确定
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import request from '@/api/request';
import QRCode from 'qrcode';
import { nextTick, onMounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { addClassAssistant, removeClassAssistant } from '@/api/class';

const router = useRouter();
const route = useRoute();
const classId = Number(route.params.id);
const qrCanvas = ref<HTMLCanvasElement | null>(null);

interface ClassInfo {
  id: number;
  school_name: string;
  session: string;
  class_name: string;
  description?: string;
  status: boolean;
  qr_code: string;
  qr_url?: string;
}

interface Assistant {
  id: number;
  assistant_id: number;
  assistant_email: string;
  assistant_name: string;
  status: boolean;
  created_at: string;
}

interface Student {
  id: string;
  real_name: string;
}

const classInfo = ref<ClassInfo | null>(null);
const assistants = ref<Assistant[]>([]);
const classStudents = ref<Student[]>([]);
const showAddAssistantModal = ref(false);
const addAssistantMode = ref('student');
const selectedStudentId = ref('');
const assistantEmail = ref('');

const fetchClassInfo = async () => {
  try {
    const data = (await request.get(`/api/v1/classes/${classId}`)) as ClassInfo;
    console.log('获取到的组织详情:', data);
    classInfo.value = data;
    await nextTick();
    generateQRCode();
  } catch (error) {
    console.error('获取组织详情失败:', error);
  }
};

const fetchAssistants = async () => {
  try {
    const data = (await request.get(`/api/v1/class-assistants/class/${classId}`)) as { items: Assistant[] };
    console.log('获取到的组织助理:', data);
    assistants.value = data.items;
  } catch (error) {
    console.error('获取组织助理失败:', error);
  }
};

const fetchClassStudents = async () => {
  try {
    const data = (await request.get(`/api/v1/classes/${classId}/students`)) as { items: Student[] };
    console.log('获取到的组织成员:', data);
    classStudents.value = data.items;
  } catch (error) {
    console.error('获取组织成员失败:', error);
  }
};

const generateQRCode = async () => {
  if (!classInfo.value?.qr_url || !qrCanvas.value) return;

  try {
    console.log('开始生成二维码，数据:', classInfo.value.qr_url);
    await QRCode.toCanvas(qrCanvas.value, classInfo.value.qr_url, {
      width: 256,
      margin: 1,
      color: {
        dark: '#000000',
        light: '#FFFFFF',
      },
    });
    console.log('二维码生成成功');
  } catch (error) {
    console.error('生成二维码失败:', error);
  }
};

const addAssistant = async () => {
  try {
    let assistantId: number;
    let email: string;

    if (addAssistantMode.value === 'student') {
      if (!selectedStudentId.value) {
        alert('请选择成员');
        return;
      }
      const parsedId = Number(selectedStudentId.value);
      if (isNaN(parsedId)) {
        alert('成员未注册绑定');
        return;
      }
      assistantId = parsedId;
      email = `student${assistantId}@example.com`;
    } else {
      if (!assistantEmail.value) {
        alert('请输入邮箱');
        return;
      }
      assistantId = 1000 + Math.floor(Math.random() * 1000);
      email = assistantEmail.value;
    }

    await addClassAssistant({
      class_id: classId,
      assistant_id: assistantId,
      assistant_email: email
    });

    alert('添加组织助理成功');
    showAddAssistantModal.value = false;
    await fetchAssistants();
  } catch (error: any) {
    console.error('添加组织助理失败:', error);
    const errorMessage = error?.message || '添加组织助理失败，请稍后重试';
    alert(errorMessage);
  }
};

const removeAssistant = async (assistantId: number) => {
  if (!confirm('确定要移除该组织助理吗？')) {
    return;
  }

  try {
    await removeClassAssistant(classId, assistantId);

    alert('移除组织助理成功');
    await fetchAssistants();
  } catch (error: any) {
    console.error('移除组织助理失败:', error);
    const errorMessage = error?.message || '移除组织助理失败，请稍后重试';
    alert(errorMessage);
  }
};

watch(
  () => classInfo.value,
  async (newValue) => {
    if (newValue) {
      await nextTick();
      generateQRCode();
    }
  },
  { deep: true }
);

onMounted(async () => {
  await fetchClassInfo();
  await fetchAssistants();
  await fetchClassStudents();
});
</script>