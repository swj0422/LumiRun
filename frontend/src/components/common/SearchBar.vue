<template>
  <div class="flex items-center space-x-2">
    <div class="relative flex-grow">
      <input
        type="text"
        v-model="localKeyword"
        @input="handleInput"
        @keyup.enter="handleSearch"
        :placeholder="placeholder"
        class="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        :disabled="loading"
      />
      <button
        v-if="localKeyword"
        @click="handleClear"
        class="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
      >
        ×
      </button>
    </div>
    <button
      @click="handleSearch"
      class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
      :disabled="loading"
    >
      <span v-if="loading">搜索中...</span>
      <span v-else>搜索</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { debounce } from '@/utils';

const props = defineProps({
  modelValue: {
    type: String,
    default: '',
  },
  placeholder: {
    type: String,
    default: '请输入搜索关键词',
  },
  debounceDelay: {
    type: Number,
    default: 300,
  },
  loading: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(['update:modelValue', 'search', 'clear']);

const localKeyword = ref(props.modelValue);

// 防抖处理的搜索函数
const debouncedSearch = debounce((keyword: string) => {
  emit('search', keyword);
}, props.debounceDelay);

const handleInput = () => {
  emit('update:modelValue', localKeyword.value);
  debouncedSearch(localKeyword.value);
};

const handleSearch = () => {
  emit('search', localKeyword.value);
};

const handleClear = () => {
  localKeyword.value = '';
  emit('update:modelValue', '');
  emit('clear');
  emit('search', '');
};

// 监听props变化
watch(
  () => props.modelValue,
  (newValue) => {
    localKeyword.value = newValue;
  }
);
</script>
