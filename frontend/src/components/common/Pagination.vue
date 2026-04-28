<template>
  <div
    class="flex items-center justify-between px-4 py-3 border-t border-gray-200"
  >
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
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';

const props = defineProps({
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
});

const emit = defineEmits(['page-change', 'size-change']);

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

// 监听props变化
watch(
  () => props.pageSize,
  (newSize) => {
    localPageSize.value = newSize;
  }
);
</script>
