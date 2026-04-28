<template>
  <div
    v-if="visible"
    class="fixed inset-0 z-50 flex items-center justify-center"
  >
    <div
      class="absolute inset-0 bg-black bg-opacity-50"
      @click="handleClose"
    ></div>
    <div class="relative bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
      <div class="flex items-center justify-between p-4 border-b">
        <h3 class="text-lg font-medium text-gray-900">{{ title }}</h3>
        <button
          @click="handleClose"
          class="text-gray-400 hover:text-gray-600 focus:outline-none"
        >
          ×
        </button>
      </div>
      <div class="p-4">
        <slot></slot>
      </div>
      <div
        v-if="showFooter"
        class="flex items-center justify-end p-4 border-t space-x-2"
      >
        <button
          @click="handleCancel"
          class="px-4 py-2 border rounded-md text-gray-700 hover:bg-gray-100 focus:outline-none"
        >
          {{ cancelText }}
        </button>
        <button
          @click="handleConfirm"
          class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none"
          :disabled="loading"
        >
          <span v-if="loading">{{ loadingText }}</span>
          <span v-else>{{ confirmText }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue';

const props = defineProps({
  visible: {
    type: Boolean,
    default: false,
  },
  title: {
    type: String,
    default: '提示',
  },
  showFooter: {
    type: Boolean,
    default: true,
  },
  confirmText: {
    type: String,
    default: '确定',
  },
  cancelText: {
    type: String,
    default: '取消',
  },
  loading: {
    type: Boolean,
    default: false,
  },
  loadingText: {
    type: String,
    default: '处理中...',
  },
});

const emit = defineEmits(['close', 'cancel', 'confirm']);

const handleClose = () => {
  emit('close');
};

const handleCancel = () => {
  emit('cancel');
};

const handleConfirm = () => {
  emit('confirm');
};
</script>
