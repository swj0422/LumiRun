<template>
  <div
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
  >
    <div class="bg-white rounded-lg p-6 w-full max-w-2xl">
      <h3 class="text-lg font-bold mb-4">成员详情</h3>
      <div class="space-y-6">
        <!-- 基本信息 -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1"
              >成员姓名</label
            >
            <input
              v-model="form.real_name"
              type="text"
              class="input w-full"
              placeholder="请输入成员姓名"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1"
              >学号</label
            >
            <div class="text-sm text-gray-500 py-2">
              {{ form.student_no || '无学号' }}
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1"
              >组织</label
            >
            <div class="text-gray-700">{{ student?.class_name }}</div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1"
              >级</label
            >
            <div class="text-gray-700">{{ student?.session }}级</div>
          </div>
        </div>

        <!-- 标签管理 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2"
            >标签管理</label
          >
          <div class="flex flex-wrap gap-2">
            <span
              v-for="tag in availableStudentTags"
              :key="tag.id"
              :class="{
                'px-3 py-1 rounded-full text-sm cursor-pointer': true,
                'bg-blue-100 text-blue-800': selectedTags.includes(tag.id),
                'bg-gray-100 text-gray-800': !selectedTags.includes(tag.id),
              }"
              @click="toggleTag(tag.id)"
            >
              {{ tag.name }}
            </span>
          </div>
        </div>

        <!-- 学习特征 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1"
            >学习特征</label
          >
          <textarea
            v-model="studentNote.learning_characteristics"
            class="input w-full"
            rows="3"
            placeholder="请输入学习特征"
          ></textarea>
        </div>

        <!-- 性格建议 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1"
            >性格建议</label
          >
          <textarea
            v-model="studentNote.personality_suggestions"
            class="input w-full"
            rows="3"
            placeholder="请输入性格建议"
          ></textarea>
        </div>

        <!-- 表现总结 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1"
            >表现总结</label
          >
          <textarea
            v-model="studentNote.performance_summary"
            class="input w-full"
            rows="3"
            placeholder="请输入表现总结"
          ></textarea>
        </div>

        <!-- 操作按钮 -->
        <div class="flex justify-end space-x-3">
          <button @click="$emit('close')" class="btn-secondary">取消</button>
          <button @click="$emit('save')" class="btn-primary">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import request from '@/api/request';

const props = defineProps({
  student: {
    type: Object,
    default: null,
  },
});

const emit = defineEmits(['close', 'save']);

const form = ref({
  real_name: '',
  student_no: '',
});

const studentNote = ref({
  learning_characteristics: '',
  personality_suggestions: '',
  performance_summary: '',
});

const originalStudentNote = ref({
  learning_characteristics: '',
  personality_suggestions: '',
  performance_summary: '',
});

const studentTags = ref<any[]>([]);
const selectedTags = ref<number[]>([]);
const originalSelectedTags = ref<number[]>([]);
const availableStudentTags = ref<any[]>([]);

// 加载成员标签
const loadStudentTags = async () => {
  if (!props.student) return;

  try {
    // 获取成员标签
      const tagsResponse = await request.get(
        `/v1/students/tags/${props.student.id}`
      );
      if (Array.isArray(tagsResponse)) {
        // 响应是数组，直接使用
        studentTags.value = tagsResponse;
        selectedTags.value = studentTags.value.map((tag: any) => tag.id);
        originalSelectedTags.value = [...selectedTags.value];
      } else if (tagsResponse && typeof tagsResponse === 'object') {
        // 响应是对象，检查是否有data字段
        if (tagsResponse.data) {
          studentTags.value = tagsResponse.data;
          selectedTags.value = studentTags.value.map((tag: any) => tag.id);
          originalSelectedTags.value = [...selectedTags.value];
        }
      }

      // 获取可用标签（只获取成员标签）
      const availableTagsResponse = await request.get('/v1/tags/?type=student');
      if (Array.isArray(availableTagsResponse)) {
        // 响应是数组，直接使用
        availableStudentTags.value = availableTagsResponse;
      } else if (availableTagsResponse && typeof availableTagsResponse === 'object') {
        // 响应是对象，检查是否有items字段（标准分页格式）或data字段
        if (availableTagsResponse.items) {
          availableStudentTags.value = availableTagsResponse.items;
        } else if (availableTagsResponse.data) {
          availableStudentTags.value = availableTagsResponse.data;
        }
      }

      // 获取成员备注
      const noteResponse = await request.get(
        `/v1/students/note/${props.student.id}`
      );
      if (noteResponse && typeof noteResponse === 'object') {
        // 直接使用响应对象（API直接返回备注数据）
        const noteData = {
          learning_characteristics: noteResponse.learning_characteristics || '',
          personality_suggestions: noteResponse.personality_suggestions || '',
          performance_summary: noteResponse.performance_summary || ''
        };
        studentNote.value = { ...noteData };
        originalStudentNote.value = { ...noteData };

        // 加载标签（从备注的tags字段或从studentTags获取）
        if (noteResponse.tags) {
          try {
            const parsedTags = JSON.parse(noteResponse.tags);
            if (Array.isArray(parsedTags)) {
              selectedTags.value = parsedTags;
              originalSelectedTags.value = [...parsedTags];
            }
          } catch (e) {
            console.error('解析标签失败:', e);
          }
        }
      }
  } catch (error) {
    console.error('加载成员标签失败:', error);
  }
};

// 切换标签
const toggleTag = (tagId: number) => {
  const index = selectedTags.value.indexOf(tagId);
  if (index > -1) {
    selectedTags.value.splice(index, 1);
  } else {
    selectedTags.value.push(tagId);
  }
};

// 获取选中的标签
defineExpose({
  getSelectedTags: () => selectedTags.value,
  getOriginalSelectedTags: () => originalSelectedTags.value,
  getStudentNote: () => studentNote.value,
  getOriginalStudentNote: () => originalStudentNote.value,
  getForm: () => form.value
});

// 监听学生变化
watch(
  () => props.student,
  (newStudent) => {
    if (newStudent) {
      form.value.real_name = newStudent.name_in_class || newStudent.real_name || '';
      form.value.student_no = newStudent.student_no_in_class || newStudent.student_no || '';
      loadStudentTags();
    }
  },
  { immediate: true }
);

onMounted(() => {
  if (props.student) {
    loadStudentTags();
  }
});
</script>
