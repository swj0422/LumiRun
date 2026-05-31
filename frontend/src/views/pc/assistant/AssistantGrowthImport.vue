<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-900">批量导入成长值</h1>
      <router-link to="/assistant/growth" class="btn-secondary">
        返回
      </router-link>
    </div>

    <div class="bg-white shadow rounded-lg p-6">
      <h3 class="text-lg font-semibold text-gray-900 mb-4">导入说明</h3>
      <ul class="list-disc pl-5 space-y-2 text-gray-600">
        <li>请下载模板文件，按照模板格式填写成员成长值</li>
        <li>模板中的成员信息必须与系统中的一致</li>
        <li>成长值可以为正数或负数</li>
        <li>导入后将自动创建成长记录</li>
      </ul>

      <div class="mt-6 space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            选择组织
          </label>
          <select v-model="selectedClassId" class="input" required>
            <option value="">选择组织</option>
            <option v-for="classItem in classes" :key="classItem.id" :value="classItem.id">
              {{ classItem.school_name }} {{ classItem.session }}级 {{ classItem.class_name }}班
            </option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            下载模板
          </label>
          <a
            :href="`/api/v1/growth/import-template?class_id=${selectedClassId}`"
            class="inline-block btn-secondary"
            :disabled="!selectedClassId"
          >
            下载模板
          </a>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            上传文件
          </label>
          <input
            type="file"
            accept=".xlsx,.xls"
            @change="handleFileChange"
            class="input"
          />
        </div>

        <div v-if="file" class="mt-2">
          <p class="text-sm text-gray-600">
            已选择文件: {{ file.name }}
          </p>
        </div>

        <div class="mt-4">
          <button
            @click="handleImport"
            class="btn-primary"
            :disabled="!selectedClassId || !file"
          >
            开始导入
          </button>
        </div>
      </div>
    </div>

    <!-- 导入结果 -->
    <div v-if="importResult" class="bg-white shadow rounded-lg p-6">
      <h3 class="text-lg font-semibold text-gray-900 mb-4">导入结果</h3>
      <div class="space-y-2">
        <p class="text-gray-600">
          成功导入: {{ importResult.success_count }} 条
        </p>
        <p class="text-gray-600">
          失败导入: {{ importResult.failed_count }} 条
        </p>
        <div v-if="importResult.failed_items && importResult.failed_items.length > 0">
          <h4 class="font-medium text-gray-800 mt-4">失败原因</h4>
          <ul class="list-disc pl-5 space-y-1 text-red-600">
            <li v-for="(item, index) in importResult.failed_items" :key="index">
              {{ item.row }}行: {{ item.error }}
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { getUserAssistantClasses } from '@/api/class';
import request from '@/api/request';

const classes = ref<any[]>([]);
const selectedClassId = ref('');
const file = ref<File | null>(null);
const importResult = ref<any>(null);

// 获取授权组织列表
const fetchClasses = async () => {
  try {
    const data = await getUserAssistantClasses();
    classes.value = (data as any).items || [];
  } catch (error) {
    console.error('获取授权组织失败:', error);
    classes.value = [];
  }
};

// 处理文件选择
const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    file.value = target.files[0];
  }
};

// 处理导入
const handleImport = async () => {
  if (!selectedClassId.value || !file.value) {
    alert('请选择组织和文件');
    return;
  }

  const formData = new FormData();
  formData.append('file', file.value);
  formData.append('class_id', selectedClassId.value);

  try {
    const response = await request.post('/api/v1/growth/batch-import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    importResult.value = response;
    alert('导入完成');
  } catch (error) {
    console.error('导入失败:', error);
    alert('导入失败，请稍后重试');
  }
};

onMounted(async () => {
  await fetchClasses();
});
</script>
