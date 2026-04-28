<template>
  <div class="space-y-6">
    <!-- 页签切换 -->
    <div class="border-b border-gray-200">
      <nav class="flex -mb-px space-x-8">
        <button
          @click="activeTab = 'records'"
          :class="{
            'py-4 px-1 border-b-2 font-medium text-sm': true,
            'border-primary-500 text-primary-600': activeTab === 'records',
            'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300':
              activeTab !== 'records',
          }"
        >
          成长记录
        </button>
        <button
          @click="activeTab = 'leaderboard'"
          :class="{
            'py-4 px-1 border-b-2 font-medium text-sm': true,
            'border-primary-500 text-primary-600': activeTab === 'leaderboard',
            'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300':
              activeTab !== 'leaderboard',
          }"
        >
          成长排行
        </button>
        <button
          @click="activeTab = 'history'"
          :class="{
            'py-4 px-1 border-b-2 font-medium text-sm': true,
            'border-primary-500 text-primary-600': activeTab === 'history',
            'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300':
              activeTab !== 'history',
          }"
        >
          成长日志
        </button>
      </nav>
    </div>

    <!-- 成长记录页签 -->
    <div v-show="activeTab === 'records'" class="space-y-6">
      <div class="flex justify-between items-center">
        <h1 class="text-2xl font-bold text-gray-900">成长记录</h1>
        <div class="flex space-x-3">
          <button
            @click="
              async () => {
                await refreshTags();
                showSingleAddModal = true;
              }
            "
            class="btn-primary"
          >
            单个录入
          </button>
          <button
            @click="
              async () => {
                await refreshTags();
                showBatchAddModal = true;
              }
            "
            class="btn-secondary"
          >
            批量导入
          </button>
        </div>
      </div>

      <!-- 搜索和筛选 -->
      <div class="bg-white rounded-lg shadow p-4 space-y-4">
        <div class="flex items-center gap-4">
          <div class="w-48 min-w-[150px]">
            <input
              v-model="searchKeyword"
              type="text"
              class="input w-full"
              placeholder="搜索学员姓名"
              @input="handleSearch"
            />
          </div>
          <select
            v-model="selectedClassId"
            class="input w-48"
            @change="fetchLogs"
          >
            <option value="">全部班级</option>
            <option
              v-for="cls in classes"
              :key="cls.id"
              :value="cls.id"
            >
              {{ cls.school_name }} {{ cls.session }}级 {{ cls.class_name }}班
            </option>
          </select>
          <select v-model="selectedType" class="input w-32" @change="fetchLogs">
            <option value="">全部类型</option>
            <option value="positive">加分</option>
            <option value="negative">减分</option>
          </select>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-sm text-gray-600">日期范围：</span>
          <input
            v-model="startDate"
            type="date"
            class="input w-40"
            @change="fetchLogs"
            placeholder="开始日期"
          />
          <span>至</span>
          <input
            v-model="endDate"
            type="date"
            class="input w-40"
            @change="fetchLogs"
            placeholder="结束日期"
          />
        </div>
      </div>

      <!-- 成长值记录列表 -->
      <div class="bg-white rounded-lg shadow overflow-hidden">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                学员
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                班级
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                变动值
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                原因
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                录入方式
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                操作人
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                创建时间
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                操作
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="log in logs" :key="log.id">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ log.student_name }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ log.class_name }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="
                    log.change_score > 0 ? 'text-green-600' : 'text-red-600'
                  "
                  class="text-sm font-medium"
                >
                  {{ log.change_score > 0 ? '+' : '' }}{{ log.change_score }}
                </span>
              </td>
              <td class="px-6 py-4 text-sm text-gray-500">
                {{ log.reason }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ log.input_type_name }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ log.operator_name || '' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(log.created_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <button
                  @click="editLog(log)"
                  class="text-primary-600 hover:text-primary-900 mr-3"
                >
                  编辑
                </button>
                <button
                  @click="openDeleteModal(log)"
                  class="text-red-600 hover:text-red-900"
                >
                  删除
                </button>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- 空状态 -->
        <div v-if="logs.length === 0" class="text-center py-12">
          <p class="text-gray-500">暂无成长值记录</p>
        </div>

        <!-- 分页 -->
        <div
          v-if="logs.length > 0"
          class="px-6 py-4 flex items-center justify-between border-t border-gray-200"
        >
          <div class="text-sm text-gray-700">
            显示 {{ skip + 1 }} 到 {{ Math.min(skip + limit, total) }} 共
            {{ total }} 条记录
          </div>
          <div class="flex gap-2">
            <button
              @click="handlePageChange(skip - limit)"
              :disabled="skip === 0"
              class="px-3 py-1 border rounded-md text-sm disabled:opacity-50"
            >
              上一页
            </button>
            <button
              @click="handlePageChange(skip + limit)"
              :disabled="skip + limit >= total"
              class="px-3 py-1 border rounded-md text-sm disabled:opacity-50"
            >
              下一页
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 成长排行页签 -->
    <div v-show="activeTab === 'leaderboard'" class="mt-8">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-xl font-bold text-gray-900">成长排行</h2>
        <button
          @click="showExportModal = true"
          class="btn-secondary flex items-center gap-2"
        >
          <svg
            class="w-4 h-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          导出
        </button>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div
          v-for="cls in classes"
          :key="cls.id"
          :ref="
            (el) => {
              if (el) classLeaderboardRefs[cls.id] = el;
            }
          "
          :data-class-id="cls.id"
          class="bg-white rounded-lg shadow overflow-hidden"
        >
          <div class="px-4 py-3 bg-gray-50 border-b border-gray-200">
            <h3 class="text-sm font-semibold text-gray-900 truncate">
              {{ cls.session || '' }}级 {{ cls.class_name }}班级
            </h3>
          </div>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th
                    class="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    排名
                  </th>
                  <th
                    class="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    学员
                  </th>
                  <th
                    class="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    总成长值
                  </th>
                  <th
                    class="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    可用成长值
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr
                  v-for="(student, index) in getClassLeaderboard(cls.id)"
                  :key="student.id"
                  :class="index < 3 ? 'bg-yellow-50' : ''"
                >
                  <td class="px-4 py-2 whitespace-nowrap text-center">
                    <div class="flex items-center justify-center">
                      <div
                        v-if="index === 0"
                        class="w-8 h-8 flex items-center justify-center"
                      >
                        <svg
                          class="w-6 h-6 text-yellow-500"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path
                            d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
                          />
                        </svg>
                      </div>
                      <div
                        v-else-if="index === 1"
                        class="w-8 h-8 flex items-center justify-center"
                      >
                        <svg
                          class="w-6 h-6 text-gray-400"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path
                            d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
                          />
                        </svg>
                      </div>
                      <div
                        v-else-if="index === 2"
                        class="w-8 h-8 flex items-center justify-center"
                      >
                        <svg
                          class="w-6 h-6 text-amber-700"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path
                            d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
                          />
                        </svg>
                      </div>
                      <span
                        v-else
                        :class="{
                          'w-6 h-6 rounded-full flex items-center justify-center font-bold text-white text-xs bg-gray-200 text-gray-700': true,
                        }"
                      >
                        {{ index + 1 }}
                      </span>
                    </div>
                  </td>
                  <td
                    class="px-4 py-2 whitespace-nowrap text-sm text-gray-900 text-center"
                  >
                    {{ student.real_name }}
                  </td>
                  <td
                    class="px-4 py-2 whitespace-nowrap text-sm text-gray-900 font-bold text-center"
                  >
                    {{ student.total_score }}
                  </td>
                  <td
                    class="px-4 py-2 whitespace-nowrap text-sm text-gray-900 text-center"
                  >
                    {{ student.available_score }}
                  </td>
                </tr>
                <tr v-if="getClassLeaderboard(cls.id).length === 0">
                  <td
                    colspan="4"
                    class="px-4 py-6 text-center text-gray-500 text-sm"
                  >
                    暂无学员数据
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- 成长日志页签 -->
    <div v-show="activeTab === 'history'" class="space-y-6">
      <div class="flex justify-between items-center">
        <h1 class="text-2xl font-bold text-gray-900">成长日志</h1>
      </div>

      <!-- 搜索和筛选 -->
      <div class="bg-white rounded-lg shadow p-4 space-y-4">
        <div class="flex items-center gap-2">
          <span class="text-sm text-gray-600">学员姓名：</span>
          <input
            v-model="historyStudentName"
            type="text"
            class="input w-40"
            @input="handleHistorySearch"
            placeholder="输入学员姓名搜索"
          />
          <span class="text-sm text-gray-600 ml-4">日期范围：</span>
          <input
            v-model="historyStartDate"
            type="date"
            class="input w-40"
            @change="fetchGrowthHistory"
            placeholder="开始日期"
          />
          <span>至</span>
          <input
            v-model="historyEndDate"
            type="date"
            class="input w-40"
            @change="fetchGrowthHistory"
            placeholder="结束日期"
          />
        </div>
      </div>

      <!-- 成长值变更流水列表 -->
      <div class="bg-white rounded-lg shadow overflow-hidden">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th
                class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                学员
              </th>
              <th
                class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                变动值
              </th>
              <th
                class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                原因
              </th>
              <th
                class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                时间
              </th>
              <th
                class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                操作类型
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="record in growthHistory" :key="record.id">
              <td
                class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-center"
              >
                {{ record.student_name }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center">
                <span
                  :class="
                    record.change_score > 0 ? 'text-green-600' : 'text-red-600'
                  "
                  class="text-sm font-medium"
                >
                  {{ record.change_score > 0 ? '+' : ''
                  }}{{ record.change_score }}
                </span>
              </td>
              <td class="px-6 py-4 text-sm text-gray-500 text-center">
                {{ record.reason }}
              </td>
              <td
                class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 text-center"
              >
                {{ formatDate(record.created_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center">
                <span
                  :class="getActionClass(record)"
                  class="text-sm font-medium"
                >
                  {{ getActionType(record) }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- 空状态 -->
        <div v-if="growthHistory.length === 0" class="text-center py-12">
          <p class="text-gray-500">暂无成长值变更记录</p>
        </div>

        <!-- 分页 -->
        <div
          v-if="growthHistory.length > 0"
          class="px-6 py-4 flex items-center justify-between border-t border-gray-200"
        >
          <div class="text-sm text-gray-700">
            显示 {{ historySkip + 1 }} 到
            {{ Math.min(historySkip + historyLimit, historyTotal) }} 共
            {{ historyTotal }} 条记录
          </div>
          <div class="flex gap-2">
            <button
              @click="handleHistoryPageChange(historySkip - historyLimit)"
              :disabled="historySkip === 0"
              class="px-3 py-1 border rounded-md text-sm disabled:opacity-50"
            >
              上一页
            </button>
            <button
              @click="handleHistoryPageChange(historySkip + historyLimit)"
              :disabled="historySkip + historyLimit >= historyTotal"
              class="px-3 py-1 border rounded-md text-sm disabled:opacity-50"
            >
              下一页
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 单个录入弹窗 -->
    <div
      v-if="showSingleAddModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg p-6 w-full max-w-lg">
        <h2 class="text-xl font-bold mb-4">单个录入</h2>

        <form @submit.prevent="handleAddGrowth">
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1"
                >选择班级</label
              >
              <select
                v-model="growthForm.class_id"
                required
                class="input"
                @change="handleClassChange"
              >
                <option value="">请选择班级</option>
                <option v-for="cls in classes" :key="cls.id" :value="cls.id">
                  {{ cls.school_name }} {{ cls.session }}级 {{ cls.class_name }}班
                </option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1"
                >选择学员</label
              >
              <div class="relative">
                <input
                  type="text"
                  v-model="studentSearch"
                  placeholder="输入学员姓名搜索..."
                  class="input w-full"
                  @focus="showStudentDropdown = true"
                  @blur="handleBlur"
                />
                <div
                  v-if="showStudentDropdown && filteredStudents.length > 0"
                  class="absolute z-10 w-full max-h-60 overflow-y-auto bg-white border border-gray-300 rounded-md shadow-lg"
                >
                  <div
                    v-for="student in filteredStudents"
                    :key="student.id"
                    class="px-3 py-2 hover:bg-gray-100 cursor-pointer"
                    @mousedown="
                      () => {
                        growthForm.student_id = String(student.id);
                        studentSearch = student.real_name;
                        showStudentDropdown = false;
                      }
                    "
                  >
                    {{ student.real_name }}
                  </div>
                </div>
                <div
                  v-else-if="
                    showStudentDropdown && filteredStudents.length === 0
                  "
                  class="absolute z-10 w-full bg-white border border-gray-300 rounded-md shadow-lg p-3 text-gray-500"
                >
                  未找到匹配的学员
                </div>
                <input type="hidden" v-model="growthForm.student_id" />
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1"
                >调整值</label
              >
              <input
                v-model.number="growthForm.score"
                type="number"
                required
                class="input"
                placeholder="正数加分，负数减分"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1"
                >原因</label
              >
              <input
                v-model="growthForm.reason"
                type="text"
                required
                class="input"
                placeholder="请输入原因"
              />
            </div>
          </div>
          <div class="flex justify-end space-x-3 mt-6">
            <button
              type="button"
              @click="showSingleAddModal = false"
              class="btn-secondary"
            >
              取消
            </button>
            <button type="submit" class="btn-primary">确认</button>
          </div>
        </form>
      </div>
    </div>

    <!-- 批量导入弹窗 -->
    <div
      v-if="showBatchAddModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg p-6 w-full max-w-lg">
        <h2 class="text-xl font-bold mb-4">批量导入</h2>

        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1"
              >选择班级</label
            >
            <select v-model="batchForm.class_id" required class="input" @change="handleBatchClassChange">
              <option value="">请选择班级</option>
              <option v-for="cls in classes" :key="cls.id" :value="cls.id">
                {{ cls.school_name }} {{ cls.session }}级 {{ cls.class_name }}班
              </option>
            </select>
          </div>
          <div class="flex gap-2">
            <button
              type="button"
              @click="downloadBatchTemplate"
              class="btn-secondary"
            >
              下载模板
            </button>
            <input
              ref="batchFileInput"
              type="file"
              accept=".xlsx,.xls"
              class="hidden"
              @change="handleBatchFileUpload"
            />
            <button
              type="button"
              @click="(batchFileInput as HTMLInputElement).click()"
              class="btn-secondary"
            >
              {{ batchFileName || '选择文件' }}
            </button>
          </div>
          <div v-if="batchFileName" class="text-sm text-gray-500">
            已选择: {{ batchFileName }}
          </div>
        </div>
        <div class="flex justify-end space-x-3 mt-6">
          <button
            type="button"
            @click="showBatchAddModal = false"
            class="btn-secondary"
          >
            取消
          </button>
          <button type="button" @click="handleBatchImport" class="btn-primary" :disabled="!batchFile">
            导入
          </button>
        </div>
      </div>
    </div>

    <!-- 编辑弹窗 -->
    <div
      v-if="showEditModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 class="text-xl font-bold mb-4">编辑成长值记录</h2>
        <form @submit.prevent="handleEditGrowth">
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1"
                >学员</label
              >
              <div class="text-sm text-gray-900">
                {{ editForm.student_name }}
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1"
                >变动值</label
              >
              <input
                v-model.number="editForm.score"
                type="number"
                required
                class="input"
                placeholder="正数加分，负数减分"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1"
                >原因</label
              >
              <input
                v-model="editForm.reason"
                type="text"
                required
                class="input"
                placeholder="请输入原因"
              />
              <!-- 成长标签快捷选项 -->
              <div v-if="growthTags.length > 0" class="mt-2">
                <div class="flex flex-wrap gap-2">
                  <button
                    v-for="tag in growthTags"
                    :key="tag.id"
                    type="button"
                    @click="
                      ((editForm.reason = tag.name),
                      (editForm.score = Number(tag.description)))
                    "
                    class="px-3 py-1 bg-gray-100 rounded-md text-sm hover:bg-gray-200 cursor-pointer"
                  >
                    {{ tag.name }} ({{ tag.description }})
                  </button>
                </div>
              </div>
            </div>
          </div>
          <div class="flex justify-end space-x-3 mt-6">
            <button
              type="button"
              @click="showEditModal = false"
              class="btn-secondary"
            >
              取消
            </button>
            <button type="submit" class="btn-primary">保存</button>
          </div>
        </form>
      </div>
    </div>

    <!-- 删除弹窗 -->
    <div
      v-if="showDeleteModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 class="text-xl font-bold mb-4">删除成长值记录</h2>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">学员</label>
            <div class="text-sm text-gray-900">
              {{ deleteForm.student_name }}
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">变动值</label>
            <div class="text-sm text-gray-900">
              {{ deleteForm.change_score }}
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">原因</label>
            <div class="text-sm text-gray-900">
              {{ deleteForm.reason }}
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1" for="delete-reason">删除原因</label>
            <textarea
              id="delete-reason"
              v-model="deleteReason"
              rows="3"
              required
              class="input"
              placeholder="请输入删除原因"
            ></textarea>
          </div>
        </div>
        <div class="flex justify-end space-x-3 mt-6">
          <button
            type="button"
            @click="showDeleteModal = false; deleteReason = ''"
            class="btn-secondary"
          >
            取消
          </button>
          <button type="button" @click="handleDeleteGrowth" class="btn-danger">
            确认删除
          </button>
        </div>
      </div>
    </div>

    <!-- 导出选择弹窗 -->
    <div
      v-if="showExportModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 class="text-xl font-bold mb-4">选择要导出的班级</h2>
        <div class="space-y-4">
          <select v-model="selectedExportClass" class="input w-full">
            <option value="">选择班级</option>
            <option value="all">全部班级</option>
            <option v-for="cls in classes" :key="cls.id" :value="cls.id">
              {{ cls.session || '' }}级 {{ cls.class_name }}班
            </option>
          </select>
        </div>
        <div class="flex justify-end space-x-3 mt-6">
          <button
            type="button"
            @click="showExportModal = false"
            class="btn-secondary"
          >
            取消
          </button>
          <button
            type="button"
            @click="handleExport"
            :disabled="!selectedExportClass"
            class="btn-primary disabled:opacity-50"
          >
            确定
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import request from '@/api/request';
import { getUserAssistantClasses } from '@/api/class';
import { debounce } from '@/utils/debounce';
import * as XLSX from 'xlsx-js-style';
import { useUserStore } from '@/stores/user';

interface GrowthLog {
  id: number;
  student_name: string;
  class_name: string;
  change_score: number;
  reason: string;
  input_type_name: string;
  created_at: string;
  updated_at?: string;
  operator_name?: string;
  class_id?: string;
  class_student_id?: string;
  change_value?: number;
}

interface GrowthHistoryRecord {
  id: number;
  operator: string;
  action: string;
  student_name: string;
  change_score: number;
  reason: string;
  created_at: string;
}

interface ClassInfo {
  id: number;
  class_name: string;
  school_name?: string;
  session?: string;
}

interface Student {
  id: number;
  real_name: string;
  student_no_in_class?: string;
  class_name?: string;
  session?: string;
  school_name?: string;
  name_in_class?: string;
}

interface Tag {
  id: number;
  name: string;
  type: string;
  description: string;
  created_at: string;
  updated_at: string;
}

const route = useRoute();
const userStore = useUserStore();

const logs = ref<GrowthLog[]>([]);
const classes = ref<ClassInfo[]>([]);
const students = ref<Student[]>([]);
const tags = ref<Tag[]>([]);
const searchKeyword = ref('');
const selectedClassId = ref('');
const selectedType = ref('');
const startDate = ref('');
const endDate = ref('');
const skip = ref(0);
const limit = ref(20);
const total = ref(0);
const showSingleAddModal = ref(false);
const showBatchAddModal = ref(false);
const growthForm = ref({
  class_id: '',
  student_id: '',
  score: 0,
  reason: '',
});

const studentSearch = ref('');
const showStudentDropdown = ref(false);

const batchForm = ref({
  class_id: '',
});
const batchFileName = ref('');
const batchFile = ref<File | null>(null);
const batchFileInput = ref<HTMLInputElement | null>(null);

const showEditModal = ref(false);
const editForm = ref({
  id: 0,
  student_name: '',
  score: 0,
  reason: '',
});

// 删除相关变量
const showDeleteReason = ref(false);
const deleteReason = ref('');
const showDeleteModal = ref(false);
const deleteForm = ref({
  id: 0,
  student_name: '',
  change_score: 0,
  reason: '',
});

const activeTab = ref('records');

// 排行榜相关变量
const classLeaderboards = ref<{
  [classId: number]: Array<{
    id: number;
    real_name: string;
    class_name: string;
    total_score: number;
    available_score: number;
  }>;
}>({});

const classLeaderboardRefs = ref<{
  [classId: number]: any;
}>({});

const selectedExportClass = ref('');
const showExportModal = ref(false);

// 成长日志相关变量
const growthHistory = ref<GrowthHistoryRecord[]>([]);
const historyStartDate = ref('');
const historyEndDate = ref('');
const historyStudentName = ref('');
const historySkip = ref(0);
const historyLimit = ref(20);
const historyTotal = ref(0);

// 过滤学员列表（搜索）
const filteredStudents = computed(() => {
  let result = students.value;

  if (studentSearch.value) {
    const searchTerm = studentSearch.value.toLowerCase();
    result = result.filter((student) =>
      student.real_name.toLowerCase().includes(searchTerm)
    );
  }

  return result;
});

// 计算成长值标签
const growthTags = computed(() => {
  return tags.value.filter((tag) => tag.type === 'growth');
});

// 刷新标签列表
const refreshTags = async () => {
  await fetchTags();
  console.log('标签列表已刷新');
};

// 处理班级变更
const handleClassChange = async () => {
  if (!growthForm.value.class_id) {
    students.value = [];
    growthForm.value.student_id = '';
    return;
  }

  try {
    const classId = parseInt(growthForm.value.class_id as string);
    const data = await request.get(`/api/v1/classes/${classId}/students`);
    if (data && (data as any).items) {
      students.value = (data as any).items.map((item: any) => ({
        id: item.id,
        real_name: item.real_name || item.name_in_class,
        student_no_in_class: item.student_no_in_class || '',
      }));
    } else {
      students.value = [];
    }
    growthForm.value.student_id = '';
    studentSearch.value = '';
  } catch (error) {
    console.error('获取班级学生失败:', error);
    students.value = [];
  }
};

// 获取标签列表
const fetchTags = async () => {
  try {
    console.log('开始获取标签列表');
    // 添加时间戳参数，防止浏览器缓存
    const timestamp = new Date().getTime();
    const data: any = await request.get(`/api/v1/tags/?t=${timestamp}`);
    console.log('获取到的标签数据:', data);
    // 后端返回对象格式，包含items和total字段
    if (data && data.items) {
      tags.value = data.items;
    } else if (Array.isArray(data)) {
      tags.value = data;
    } else {
      tags.value = [];
    }
    console.log('处理后的标签数据:', tags.value);
    console.log(
      '成长标签数量:',
      tags.value.filter((tag) => tag.type === 'growth').length
    );
  } catch (error) {
    console.error('获取标签列表失败:', error);
    tags.value = [];
  }
};

// 获取班级学员列表（用于批量导入模板下载）
const fetchStudents = async () => {
  if (!batchForm.value.class_id) {
    students.value = [];
    return;
  }

  try {
    const classId = parseInt(batchForm.value.class_id as string);
    const data = await request.get(`/api/v1/classes/${classId}/students`);
    if (data && (data as any).items) {
      students.value = (data as any).items.map((item: any) => ({
        id: item.id,
        real_name: item.real_name || item.name_in_class,
        student_no_in_class: item.student_no_in_class || '',
        class_name: item.class_name || '',
        session: item.session || '',
        school_name: item.school_name || '',
      }));
    } else {
      students.value = [];
    }
  } catch (error) {
    console.error('获取班级学生失败:', error);
    students.value = [];
  }
};

// 处理批量导入班级变更
const handleBatchClassChange = async () => {
  batchFileName.value = '';
  batchFile.value = null;
  // 自动获取该班级的学员列表
  await fetchStudents();
};

// 处理输入框失焦
const handleBlur = () => {
  setTimeout(() => {
    showStudentDropdown.value = false;
  }, 200);
};

// 获取授权班级列表
const fetchClasses = async () => {
  try {
    const data = await getUserAssistantClasses();
    classes.value = (data as any).items || [];
    // 自动选择第一个班级
    if (classes.value.length > 0) {
      const firstClassId = classes.value[0].id;
      selectedClassId.value = firstClassId;
      growthForm.value.class_id = firstClassId;
      batchForm.value.class_id = firstClassId;
      // 触发获取该班级的学员列表
      await handleClassChange();
      // 批量导入也需要获取学员列表
      await fetchStudents();
    }
  } catch (error) {
    console.error('获取授权班级失败:', error);
    classes.value = [];
  }
};

const fetchLogs = async () => {
  try {
    const params = new URLSearchParams();
    if (searchKeyword.value) {
      params.append('student_name', searchKeyword.value.trim());
    }
    if (selectedClassId.value) {
      params.append('class_id', selectedClassId.value);
    }
    if (selectedType.value) {
      params.append('change_type', selectedType.value);
    }
    if (startDate.value) {
      params.append('start_time', new Date(startDate.value).toISOString());
    }
    if (endDate.value) {
      params.append('end_time', new Date(endDate.value).toISOString());
    }
    params.append('skip', skip.value.toString());
    params.append('limit', limit.value.toString());
    params.append('identity', 'assistant');
    params.append('t', new Date().getTime().toString());

    const data: any = await request.get(`/api/v1/growth/logs?${params.toString()}`);
    logs.value = data?.items || [];
    total.value = data?.total || 0;
  } catch (error) {
    console.error('获取成长值记录失败:', error);
  }
};

const handleSearch = () => {
  skip.value = 0;
  fetchLogs();
};

const handlePageChange = (newSkip: number) => {
  if (newSkip >= 0) {
    skip.value = newSkip;
    fetchLogs();
  }
};

const formatDate = (date: string) => {
  return new Date(date).toLocaleString('zh-CN');
};

// 获取操作类型
const getActionType = (record: GrowthHistoryRecord) => {
  if (record.reason.includes('兑换')) {
    return '兑换';
  }
  if (record.reason.includes('删除：')) {
    return '删除';
  }
  if (record.action === 'add') {
    return '添加';
  } else if (record.action === 'update') {
    return '更新';
  }
  return record.action;
};

// 获取操作类型的样式类
const getActionClass = (record: GrowthHistoryRecord) => {
  if (record.reason.includes('兑换')) {
    return 'text-blue-600';
  }
  if (record.reason.includes('删除：')) {
    return 'text-red-600';
  }
  return record.action === '添加' ? 'text-green-600' : 'text-red-600';
};

const handleAddGrowth = async () => {
  try {
    if (!growthForm.value.class_id) {
      alert('请选择班级');
      return;
    }
    if (!growthForm.value.student_id) {
      alert('请选择学员');
      return;
    }

    const selectedStudent = students.value.find(
      (s) => String(s.id) === growthForm.value.student_id
    );
    if (!selectedStudent) {
      alert('学员信息获取失败，请重新选择');
      return;
    }

    const response = await request.post('/api/v1/growth/record', {
      student_name: selectedStudent.real_name,
      class_id: growthForm.value.class_id,
      change_score: growthForm.value.score,
      reason: growthForm.value.reason,
      input_type: 1,
    });

    growthForm.value = {
      class_id: '',
      student_id: '',
      score: 0,
      reason: '',
    };
    studentSearch.value = '';
    showSingleAddModal.value = false;

    // 获取当前用户的真实姓名
    const operatorName = userStore.userInfo?.real_name || '';

    // 将新添加的记录添加到列表开头
    if (response) {
      logs.value.unshift({
        ...response,
        student_name: selectedStudent.real_name,
        class_name: selectedStudent.class_name || '',
        change_score: growthForm.value.score,
        reason: growthForm.value.reason,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        input_type_name: '手动录入',
        operator_name: operatorName,
        action: '添加',
      });
    }

    // 刷新排行榜数据，因为成长值可能改变了
    fetchClassLeaderboard();

    alert('添加成功');
    await fetchLogs();
    await fetchGrowthHistory();
  } catch (error) {
    console.error('添加成长值失败:', error);
    alert('添加失败，请稍后重试');
  }
};

const editLog = (log: GrowthLog) => {
  editForm.value = {
    id: log.id,
    student_name: log.student_name,
    score: log.change_score,
    reason: log.reason,
  };
  showEditModal.value = true;
};

const openDeleteModal = (log: GrowthLog) => {
  deleteForm.value = {
    id: log.id,
    student_name: log.student_name,
    change_score: log.change_score,
    reason: log.reason,
  };
  deleteReason.value = '';
  showDeleteModal.value = true;
};

const handleEditGrowth = async () => {
  try {
    console.log('开始修改成长值记录:', editForm.value);
    const response = await request.put(`/api/v1/growth/logs/${editForm.value.id}`, {
      change_score: editForm.value.score,
      reason: editForm.value.reason,
    });
    console.log('修改成功，响应:', response);
    showEditModal.value = false;

    // 获取当前用户的真实姓名
    const operatorName = userStore.userInfo?.real_name || '';

    // 更新原记录
    if (response && response.log) {
      const updatedLog = response.log;

      // 更新原记录
      const index = logs.value.findIndex((log) => log.id === updatedLog.id);
      if (index !== -1) {
        // 获取班级信息
        const selectedClass = classes.value.find(
          (cls) => String(cls.id) === updatedLog.class_id
        );
        const className = selectedClass ? selectedClass.class_name : '';

        // 获取学员信息
        const selectedStudent = students.value.find(
          (s) => s.id === updatedLog.class_student_id
        );
        const studentName = selectedStudent
          ? selectedStudent.name_in_class || selectedStudent.real_name
          : '';

        logs.value[index] = {
          ...updatedLog,
          student_name: studentName,
          class_name: className,
          change_score: updatedLog.change_value || updatedLog.change_score,
          reason: updatedLog.reason,
          updated_at: new Date().toISOString(),
          input_type_name: '手动录入',
          operator_name: operatorName,
          action: '添加',
        };
      }
    }

    // 刷新排行榜数据，因为成长值可能改变了
    fetchClassLeaderboard();

    alert('修改成功');
    await fetchLogs();
    await fetchGrowthHistory();
  } catch (error: any) {
    console.error('修改成长值记录失败:', error);
    console.error('错误响应:', error.response);
    console.error('错误状态:', error.response?.status);
    console.error('错误数据:', error.response?.data);
    alert('修改失败，请稍后重试');
  }
};

const handleDeleteGrowth = async () => {
  try {
    if (!deleteReason.value) {
      alert('请输入删除原因');
      return;
    }

    // 发送删除请求
    const response = await request.delete(`/api/v1/growth/logs/${deleteForm.value.id}`, {
      data: {
        reason: deleteReason.value
      }
    });

    console.log('删除成功，响应:', response);

    // 保存删除原因，因为后面会重置
    const finalDeleteReason = deleteReason.value;

    // 关闭删除弹窗并重置状态
    showDeleteModal.value = false;
    deleteReason.value = '';

    // 从列表中移除被删除的记录
    const index = logs.value.findIndex((log) => log.id === deleteForm.value.id);
    if (index !== -1) {
      logs.value.splice(index, 1);
    }

    // 刷新排行榜数据，因为成长值可能改变了
    fetchClassLeaderboard();

    // 刷新成长记录列表和成长日志，确保显示最新数据
    fetchLogs();
    fetchGrowthHistory();

    alert(`删除成功，原因：${finalDeleteReason}`);
  } catch (error: any) {
    console.error('删除成长值记录失败:', error);
    console.error('错误响应:', error.response);
    console.error('错误状态:', error.response?.status);
    console.error('错误数据:', error.response?.data);
    alert('删除失败，请稍后重试');
  }
};

const handleBatchFileUpload = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    batchFile.value = target.files[0];
    batchFileName.value = target.files[0].name;
  }
};

// 下载批量导入模板
const downloadBatchTemplate = async () => {
  if (!batchForm.value.class_id) {
    alert('请先选择班级');
    return;
  }

  // 确保班级数据已加载
  if (classes.value.length === 0) {
    await fetchClasses();
  }

  // 确保学员数据已加载
  if (students.value.length === 0) {
    await fetchStudents();
  }

  console.log('班级列表:', classes.value);
  console.log('选择的班级ID:', batchForm.value.class_id);

  // 尝试多种方式查找班级
  let selectedClassInfo = classes.value.find(
    (cls) => String(cls.id) === batchForm.value.class_id
  );

  // 如果没找到，尝试直接比较数字
  if (!selectedClassInfo) {
    const classIdNum = parseInt(batchForm.value.class_id);
    selectedClassInfo = classes.value.find((cls) => cls.id === classIdNum);
  }

  console.log('找到的班级信息:', selectedClassInfo);

  if (!selectedClassInfo) {
    alert('班级信息获取失败，请重新选择');
    return;
  }

  const classDisplayText = `${selectedClassInfo.session || ''}级 ${selectedClassInfo.class_name}班 - ${selectedClassInfo.school_name || ''}`;

  // 构建模板数据
  const sheetData = [
    [classDisplayText],
    ['黄色背景行不可删除或变更，否则无法导入'],
    ['学员学号', '姓名', '成长原因', '成长值'],
  ];

  // 学员已经是通过班级ID获取的，不需要再过滤
  // 直接使用 students.value 作为该班级的学员列表
  const classStudents = [...students.value];

  console.log('过滤后的学员:', classStudents);

  // 按学号大小升序排序
  classStudents.sort((a, b) => {
    // 提取学号数字部分进行比较
    const getStudentNo = (student: any) => {
      const no = student.student_no_in_class || '';
      // 提取数字部分
      const numPart = no.match(/\d+/);
      return numPart ? parseInt(numPart[0]) : 0;
    };
    return getStudentNo(a) - getStudentNo(b);
  });

  console.log('排序后的学员:', classStudents);

  // 添加学员信息到模板
  classStudents.forEach((student) => {
    sheetData.push([
      student.student_no_in_class || '',
      student.real_name || '',
      '', // 成长原因留空，由用户填写
      '', // 成长值留空，由用户填写
    ]);
  });

  const ws = XLSX.utils.aoa_to_sheet(sheetData);

  // 设置列宽
  ws['!cols'] = [{ wch: 15 }, { wch: 10 }, { wch: 30 }, { wch: 10 }];

  // 设置黄色背景
  const yellowStyle = {
    fill: {
      fgColor: { rgb: 'FFFF00' },
    },
  };

  // 设置前3行为黄色背景
  for (let col = 0; col < 4; col++) {
    for (let row = 0; row < 3; row++) {
      const cellAddress = XLSX.utils.encode_cell({ r: row, c: col });
      if (ws[cellAddress]) ws[cellAddress].s = yellowStyle;
    }
  }

  // 提取成长标签名称
  const growthTags = tags.value
    .filter((tag) => tag.type === 'growth')
    .map((tag) => tag.name);
  console.log('成长标签:', growthTags);

  // 为标签名称列添加下拉选项
  if (growthTags.length > 0) {
    // 计算数据区域范围
    const startRow = 3; // 从第4行开始（索引为3）
    const endRow = startRow + classStudents.length - 1;
    const column = 2; // 标签名称列（索引为2）

    if (endRow >= startRow) {
      const startCell = XLSX.utils.encode_cell({ r: startRow, c: column });
      const endCell = XLSX.utils.encode_cell({ r: endRow, c: column });
      const range = `${startCell}:${endCell}`;

      console.log('数据区域范围:', range);

      // 创建数据验证规则，禁止手动输入，只能选择预设标签
      const dataValidation = {
        type: 'list',
        allowBlank: false, // 不允许空白
        formula1: '"' + growthTags.join(',') + '"',
        showDropDown: true,
        errorTitle: '输入错误',
        error: '请从下拉列表中选择预设的成长标签',
        errorStyle: 'stop', // 阻止无效输入
      };

      console.log('数据验证规则:', dataValidation);

      // 应用数据验证到标签名称列
      if (!ws['!dataValidations']) {
        ws['!dataValidations'] = { ref: range, formulas: [dataValidation] };
      } else {
        ws['!dataValidations'].ref = range;
        ws['!dataValidations'].formulas = [dataValidation];
      }
    }
  }

  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, '批量导入');

  // 下载文件
  XLSX.writeFile(wb, `成长值批量导入_${selectedClassInfo.class_name}班_${new Date().toISOString().split('T')[0]}.xlsx`);
};

const handleBatchImport = debounce(async () => {
  if (!batchForm.value.class_id) {
    alert('请先选择班级');
    return;
  }
  if (!batchFile.value) {
    alert('请选择文件');
    return;
  }

  // 尝试多种方式查找班级
  let selectedClassInfo = classes.value.find(
    (cls) => String(cls.id) === batchForm.value.class_id
  );

  // 如果没找到，尝试直接比较数字
  if (!selectedClassInfo) {
    const classIdNum = parseInt(batchForm.value.class_id);
    selectedClassInfo = classes.value.find((cls) => cls.id === classIdNum);
  }

  if (!selectedClassInfo) {
    alert('班级信息获取失败，请重新选择');
    return;
  }

  const reader = new FileReader();
  reader.onload = async (e) => {
    try {
      const data = e.target?.result as ArrayBuffer;
      const workbook = XLSX.read(data, { type: 'array' });
      const worksheet = workbook.Sheets[workbook.SheetNames[0]];

      // 获取所有数据
      const jsonData = XLSX.utils.sheet_to_json(worksheet, {
        header: 1,
      }) as any[][];

      // 跳过前三行（班级信息、说明、表头）
      const records = jsonData.slice(3);

      if (records.length === 0) {
        alert(
          '未解析到有效的成长值记录，请确保学员学号、姓名和成长原因都已填写'
        );
        return;
      }

      // 构建导入数据
      const importData = [];
      const invalidRecords = [];

      // 获取当前选择的班级信息
      let currentSelectedClassInfo = classes.value.find(
        (cls) => String(cls.id) === batchForm.value.class_id
      );
      if (!currentSelectedClassInfo) {
        const classIdNum = parseInt(batchForm.value.class_id);
        currentSelectedClassInfo = classes.value.find((cls) => cls.id === classIdNum);
      }

      for (let i = 0; i < records.length; i++) {
        const record = records[i];
        const studentNo = String(record[0] || '').trim();
        const studentName = String(record[1] || '').trim();
        const growthReason = String(record[2] || '').trim();
        const growthValueStr = String(record[3] || '').trim();

        if (!studentNo || !studentName || !growthReason) {
          invalidRecords.push(`第${i + 4}行：缺少必要信息`);
          continue;
        }

        // 验证学员是否属于当前选择的班级
        const isStudentInClass = students.value.some((student) => {
          return (
            currentSelectedClassInfo &&
            student.student_no_in_class === studentNo &&
            student.real_name === studentName &&
            student.class_name === currentSelectedClassInfo.class_name &&
            student.session === currentSelectedClassInfo.session
          );
        });

        if (!isStudentInClass) {
          invalidRecords.push(
            `第${i + 4}行：学员 ${studentName}（学号：${studentNo}）不属于当前选择的班级`
          );
          continue;
        }

        let changeScore: number;
        let reason: string;

        // 查找对应的成长标签
        const tag = tags.value.find(
          (t) => t.name === growthReason && t.type === 'growth'
        );

        if (growthValueStr) {
          // 如果填写了成长值，验证是否为整数
          const parsedValue = parseInt(growthValueStr);
          if (isNaN(parsedValue)) {
            invalidRecords.push(`第${i + 4}行：成长值必须是整数`);
            continue;
          }

          // 检查是否与成长标签一致但成长值不一致
          if (tag) {
            const tagScore = Number(tag.description);
            if (!isNaN(tagScore) && tagScore !== parsedValue) {
              // 弹出确认框让用户选择
              const useTagValue = confirm(
                `第${i + 4}行：成长原因"${growthReason}"与系统中的成长标签一致，但成长值(${parsedValue})与标签值(${tagScore})不一致。\n\n是否使用系统标签值(${tagScore})导入？\n\n点击"确定"使用标签值，点击"取消"使用表单值(${parsedValue})`
              );

              if (useTagValue) {
                changeScore = tagScore;
              } else {
                changeScore = parsedValue;
              }
            } else {
              changeScore = parsedValue;
            }
          } else {
            changeScore = parsedValue;
          }
          reason = growthReason;
        } else {
          // 如果没有填写成长值，尝试匹配成长标签
          if (tag) {
            // 匹配到成长标签，使用标签的值
            const parsedScore = Number(tag.description);
            if (isNaN(parsedScore)) {
              invalidRecords.push(
                `第${i + 4}行：成长标签"${growthReason}"的分数无效`
              );
              continue;
            }
            changeScore = parsedScore;
            reason = growthReason;
          } else {
            // 没有匹配到成长标签，且没有填写成长值，不导入
            invalidRecords.push(
              `第${i + 4}行：成长原因"${growthReason}"不是已创建的成长标签，且未填写成长值`
            );
            continue;
          }
        }

        importData.push({
          student_no: studentNo,
          student_name: studentName,
          tag_name: tag ? tag.name : null,
          change_score: changeScore,
          reason: reason,
          input_type: 1,
        });
      }

      // 显示无效记录信息
      if (invalidRecords.length > 0) {
        alert(`以下记录导入失败：\n${invalidRecords.join('\n')}`);
      }

      if (importData.length === 0) {
        alert(
          '未解析到有效的成长值记录，请确保学员学号、姓名和成长原因都已填写，且成长值为整数'
        );
        return;
      }

      // 调用批量导入接口（异步处理）
      await request.post('/api/v1/growth/batch-import', importData);

      showBatchAddModal.value = false;
      batchFile.value = null;
      batchFileName.value = '';
      batchForm.value.class_id = '';

      // 显示导入成功提示
      alert(
        `导入任务已提交：共 ${importData.length} 条记录，系统正在处理，请稍后查看导入结果`
      );

      // 刷新日志列表和排行榜数据，可能会看到部分已导入的记录
      setTimeout(() => {
        fetchLogs();
        fetchGrowthHistory();
        fetchClassLeaderboard();
      }, 1000);
    } catch (error) {
      console.error('批量导入失败:', error);
      alert('导入失败，请重试');
    }
  };
  reader.readAsArrayBuffer(batchFile.value);
}, 1000);

// 成长排行相关函数
const fetchClassLeaderboard = async () => {
  try {
    for (const cls of classes.value) {
      // 添加时间戳参数，防止浏览器缓存
      const timestamp = new Date().getTime();
      const response = (await request.get(
        `/api/v1/leaderboard/class/${cls.id}?t=${timestamp}`
      )) as Array<{
        id: number;
        real_name: string;
        class_name: string;
        total_score: number;
        available_score: number;
      }>;
      classLeaderboards.value[cls.id] = response || [];
    }
  } catch (error) {
    console.error('获取班级排行榜失败:', error);
  }
};

const getClassLeaderboard = (classId: number) => {
  return classLeaderboards.value[classId] || [];
};

// 导出功能
const handleExport = async () => {
  if (!selectedExportClass.value) {
    alert('请选择要导出的班级');
    return;
  }

  try {
    const params = new URLSearchParams();
    if (selectedExportClass.value !== 'all') {
      params.append('class_id', selectedExportClass.value);
    }

    const response = await request.get(`/api/v1/growth/export?${params.toString()}`, {
      responseType: 'blob'
    });

    const blob = new Blob([response], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `成长记录导出_${new Date().toISOString().split('T')[0]}.xlsx`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    showExportModal.value = false;
  } catch (error) {
    console.error('导出失败:', error);
    alert('导出失败，请重试');
  }
};

// 成长日志相关函数
const fetchGrowthHistory = async () => {
  try {
    const params = new URLSearchParams();
    if (historyStartDate.value) {
      params.append('start_time', new Date(historyStartDate.value).toISOString());
    }
    if (historyEndDate.value) {
      params.append('end_time', new Date(historyEndDate.value).toISOString());
    }
    if (historyStudentName.value) {
      params.append('student_name', historyStudentName.value);
    }
    params.append('skip', historySkip.value.toString());
    params.append('limit', historyLimit.value.toString());
    params.append('t', new Date().getTime().toString());

    const data: any = await request.get(`/api/v1/growth/history?${params.toString()}`);
    growthHistory.value = data?.items || [];
    historyTotal.value = data?.total || 0;
  } catch (error) {
    console.error('获取成长值变更流水失败:', error);
    growthHistory.value = [];
  }
};

const handleHistorySearch = () => {
  historySkip.value = 0;
  fetchGrowthHistory();
};

const handleHistoryPageChange = (newSkip: number) => {
  if (newSkip >= 0) {
    historySkip.value = newSkip;
    fetchGrowthHistory();
  }
};

// 监听activeTab变化，切换到不同页签时加载对应数据
watch(activeTab, (newTab) => {
  if (newTab === 'records') {
    fetchLogs();
  } else if (newTab === 'leaderboard') {
    fetchClassLeaderboard();
  } else if (newTab === 'history') {
    fetchGrowthHistory();
  }
});

onMounted(async () => {
  await fetchClasses();
  await fetchTags();
  await fetchLogs();
  await fetchGrowthHistory();
  await fetchClassLeaderboard();
});
</script>
