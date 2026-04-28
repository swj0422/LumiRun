<template>
  <div class="bg-white rounded-lg shadow overflow-hidden">
    <table class="min-w-full divide-y divide-gray-200">
      <thead class="bg-gray-50">
        <tr>
          <th
            v-for="column in columns"
            :key="column.key"
            scope="col"
            class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
          >
            {{ column.label }}
          </th>
        </tr>
      </thead>
      <tbody class="bg-white divide-y divide-gray-200">
        <template v-if="data && data.length > 0">
          <tr
            v-for="(item, index) in data"
            :key="item.id || index"
            class="hover:bg-gray-50"
          >
            <td
              v-for="column in columns"
              :key="column.key"
              class="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
            >
              <slot :name="`column-${column.key}`" :item="item" :index="index">
                {{ item[column.key] }}
              </slot>
            </td>
          </tr>
        </template>
        <template v-else>
          <tr>
            <td
              :colspan="columns.length"
              class="px-6 py-12 text-center text-gray-500"
            >
              {{ emptyText }}
            </td>
          </tr>
        </template>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { defineProps } from 'vue';

interface TableColumn {
  key: string;
  label: string;
}

const props = defineProps({
  data: {
    type: Array,
    default: () => [],
  },
  columns: {
    type: Array as () => TableColumn[],
    required: true,
  },
  emptyText: {
    type: String,
    default: '暂无数据',
  },
});
</script>
