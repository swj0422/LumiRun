<template>
  <div class="bg-white rounded-lg shadow overflow-hidden">
    <table class="min-w-full divide-y divide-gray-200">
      <thead class="bg-gray-50">
        <tr>
          <th
            scope="col"
            class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider"
          >
            序号
          </th>
          <th
            scope="col"
            class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
          >
            学员
          </th>
          <th
            scope="col"
            class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider"
          >
            班级
          </th>
          <th
            scope="col"
            class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider"
          >
            单位
          </th>
          <th
            scope="col"
            class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider"
          >
            级
          </th>
          <th
            scope="col"
            class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider"
          >
            总成长值
          </th>
          <th
            scope="col"
            class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider"
          >
            可用成长值
          </th>
          <th
            scope="col"
            class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider"
          >
            状态
          </th>
          <th
            scope="col"
            class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider"
          >
            操作
          </th>
        </tr>
      </thead>
      <tbody class="bg-white divide-y divide-gray-200">
        <template v-if="students && Array.isArray(students) && students.length > 0">
          <tr
            v-for="(student, index) in students"
            :key="student.id || index"
            :class="{
              'hover:bg-gray-50': true,
              'bg-blue-50': student.class_id % 2 === 0,
              'bg-green-50': student.class_id % 2 !== 0
            }"
          >
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              {{ (currentPage - 1) * pageSize + index + 1 }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <div>
                <div class="text-sm font-medium text-gray-900">
                  {{ student.name_in_class || student.real_name || '未知' }}
                </div>
                <div class="text-sm text-gray-500">
                  {{ student.student_no_in_class || student.student_no || '' }}
                </div>
                <div class="flex space-x-1 mt-1">
                  <span
                    v-for="tag in student.tags || []"
                    :key="tag.id || tag.name"
                    class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800"
                  >
                    {{ tag.tag_name || tag.name }}
                  </span>
                </div>
              </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 text-center">
              {{ student.class_name || '未知班级' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 text-center">
              {{ student.school_name || '未知单位' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 text-center">
              {{ student.session || '' }}级
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 text-center">
              {{ student.total_score || 0 }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 text-center">
              {{ student.available_score || 0 }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-center">
              <span
                :class="{
                  'px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full': true,
                  'bg-green-100 text-green-800': student.is_active && student.bind_status_text?.includes('已绑定'),
                  'bg-yellow-100 text-yellow-800': student.is_active && student.bind_status_text?.includes('待审核'),
                  'bg-red-100 text-red-800': !student.is_active,
                  'bg-gray-100 text-gray-800': student.bind_status_text?.includes('未绑定') || student.bind_status_text?.includes('已解绑'),
                }"
              >
                {{ student.bind_status_text || '未知' }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-center">
              <div class="flex space-x-2 justify-center">
                <button
                  @click="$emit('open-growth-modal', student)"
                  class="text-blue-600 hover:text-blue-900"
                >
                  记录
                </button>
                <button
                  @click="$emit('view-detail', student)"
                  class="text-green-600 hover:text-green-900"
                >
                  编辑
                </button>
                <div class="relative">
                  <button
                    @click="$emit('toggle-action-menu', student.id)"
                    class="text-gray-600 hover:text-gray-900"
                  >
                    更多
                  </button>
                  <div
                    v-if="activeActionMenu === student.id"
                    class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-10"
                  >
                    <button
                      v-if="student.is_active"
                      @click="$emit('stop-student', student)"
                      class="block px-4 py-2 text-sm text-red-600 hover:bg-gray-100 w-full text-left"
                    >
                      停用
                    </button>
                    <button
                      v-else
                      @click="$emit('activate-student', student)"
                      class="block px-4 py-2 text-sm text-green-600 hover:bg-gray-100 w-full text-left"
                    >
                      启用
                    </button>
                    <button
                      v-if="student.bind_status === 'approved'"
                      @click="$emit('unbind-student', student)"
                      class="block px-4 py-2 text-sm text-red-600 hover:bg-gray-100 w-full text-left"
                    >
                      解绑
                    </button>
                    <button
                      @click="$emit('delete-student', student)"
                      class="block px-4 py-2 text-sm text-red-600 hover:bg-gray-100 w-full text-left"
                    >
                      删除
                    </button>
                  </div>
                </div>
              </div>
            </td>
          </tr>
        </template>
        <template v-else>
          <tr>
            <td colspan="9" class="px-6 py-12 text-center text-gray-500">
              {{ students && !Array.isArray(students) ? '数据格式错误' : '暂无数据' }}
            </td>
          </tr>
        </template>
      </tbody>
    </table>
    <div class="px-6 py-4 border-t border-gray-200">
      <div class="flex items-center justify-between">
        <div class="text-sm text-gray-500">共 {{ total }} 条记录</div>
        <div class="flex items-center space-x-2">
          <button
            @click="handlePageChange(currentPage - 1)"
            class="px-3 py-1 border rounded text-sm"
            :disabled="currentPage === 1"
          >
            上一页
          </button>
          <span class="text-sm">{{ currentPage }} / {{ totalPages }}</span>
          <button
            @click="handlePageChange(currentPage + 1)"
            class="px-3 py-1 border rounded text-sm"
            :disabled="currentPage === totalPages"
          >
            下一页
          </button>
          <select
            v-model="localPageSize"
            @change="handleSizeChange"
            class="px-2 py-1 border rounded text-sm"
          >
            <option v-for="size in pageSizes" :key="size" :value="size">
              {{ size }} 条/页
            </option>
          </select>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';

const props = defineProps({
  students: {
    type: Array,
    default: () => [],
  },
  total: {
    type: Number,
    default: 0,
  },
  pageSize: {
    type: Number,
    default: 20,
  },
  currentPage: {
    type: Number,
    default: 1,
  },
  pageSizes: {
    type: Array,
    default: () => [10, 20, 50, 100],
  },
  activeActionMenu: {
    type: Number,
    default: null,
  },
});

const emit = defineEmits([
  'page-change',
  'size-change',
  'view-detail',
  'open-growth-modal',
  'toggle-action-menu',
  'stop-student',
  'activate-student',
  'unbind-student',
  'delete-student',
]);

const localPageSize = ref(props.pageSize);

const totalPages = computed(() => {
  return Math.ceil(props.total / props.pageSize);
});

const handlePageChange = (page: number) => {
  if (page >= 1 && page <= totalPages.value) {
    emit('page-change', page);
  }
};

const handleSizeChange = () => {
  emit('size-change', localPageSize.value);
};
</script>
