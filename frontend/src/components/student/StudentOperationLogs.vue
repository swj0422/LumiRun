<template>
  <div class="space-y-4">
    <!-- 搜索和筛选 -->
    <div class="bg-white rounded-lg shadow p-4">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <input
            v-model="localSearchKeyword"
            type="text"
            class="input w-full"
            placeholder="搜索成员姓名"
            @input="handleSearch"
          />
        </div>
        <div>
          <select
            v-model="localSelectedOperationType"
            class="input w-full"
            @change="handleSearch"
          >
            <option value="">全部操作类型</option>
            <option value="add">添加</option>
            <option value="delete">删除</option>
            <option value="unbind">解绑</option>
            <option value="tag_add">添加标签</option>
            <option value="tag_delete">删除标签</option>
            <option value="note_add">添加备注</option>
            <option value="note_update">更新备注</option>
            <option value="stop">停用</option>
            <option value="restore">恢复</option>
          </select>
        </div>
        <div>
          <input
            v-model="localStartDate"
            type="date"
            class="input w-full"
            @change="handleSearch"
          />
        </div>
        <div>
          <input
            v-model="localEndDate"
            type="date"
            class="input w-full"
            @change="handleSearch"
          />
        </div>
      </div>
    </div>

    <!-- 日志列表 -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th
              scope="col"
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              操作人
            </th>
            <th
              scope="col"
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              操作时间
            </th>
            <th
              scope="col"
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              操作类型
            </th>
            <th
              scope="col"
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              成员姓名
            </th>
            <th
              scope="col"
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              操作内容
            </th>
            <th
              scope="col"
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              操作
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="log in logs" :key="log.id" class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              {{ log.operator_name }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ log.created_at }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
              <span
                :class="{
                  'px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full': true,
                  'bg-blue-100 text-blue-800': log.operation_type === 'add',
                  'bg-red-100 text-red-800': [
                    'delete',
                    'unbind',
                    'stop',
                  ].includes(log.operation_type),
                  'bg-green-100 text-green-800':
                    log.operation_type === 'restore',
                  'bg-yellow-100 text-yellow-800': [
                    'tag_add',
                    'tag_delete',
                    'note_add',
                    'note_update',
                  ].includes(log.operation_type),
                }"
              >
                {{ getOperationTypeText(log.operation_type) }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              {{ log.student_name }}
            </td>
            <td class="px-6 py-4 text-sm text-gray-500">
              {{ log.operation_content }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
              <button
                @click="$emit('view-detail', log)"
                class="text-blue-600 hover:text-blue-900"
              >
                查看
              </button>
            </td>
          </tr>
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
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';

const props = defineProps({
  logs: {
    type: Array,
    default: () => [],
  },
  total: {
    type: Number,
    default: 0,
  },
  skip: {
    type: Number,
    default: 0,
  },
  searchKeyword: {
    type: String,
    default: '',
  },
  selectedOperationType: {
    type: String,
    default: '',
  },
  startDate: {
    type: String,
    default: '',
  },
  endDate: {
    type: String,
    default: '',
  },
});

const emit = defineEmits(['fetch-logs', 'view-detail']);

const localSearchKeyword = ref(props.searchKeyword);
const localSelectedOperationType = ref(props.selectedOperationType);
const localStartDate = ref(props.startDate);
const localEndDate = ref(props.endDate);
const currentPage = ref(Math.floor(props.skip / 20) + 1);

const totalPages = computed(() => {
  return Math.ceil(props.total / 20);
});

const getOperationTypeText = (type: string) => {
  const typeMap: Record<string, string> = {
    add: '添加',
    delete: '删除',
    unbind: '解绑',
    tag_add: '添加标签',
    tag_delete: '删除标签',
    note_add: '添加备注',
    note_update: '更新备注',
    stop: '停用',
    restore: '恢复',
  };
  return typeMap[type] || type;
};

const handleSearch = () => {
  currentPage.value = 1;
  emit('fetch-logs');
};

const handlePageChange = (page: number) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page;
    emit('fetch-logs');
  }
};

onMounted(() => {
  emit('fetch-logs');
});
</script>
