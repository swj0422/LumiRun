<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-900">系统设置</h1>
      <div class="text-sm text-gray-500">
        仅超级管理员可访问
      </div>
    </div>

    <div class="space-y-6">
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">基础设置</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">系统名称</label>
            <input v-model="settings.site_name" type="text" class="input w-full" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">系统描述</label>
            <input v-model="settings.site_description" type="text" class="input w-full" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">联系邮箱</label>
            <input v-model="settings.contact_email" type="email" class="input w-full" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">联系电话</label>
            <input v-model="settings.contact_phone" type="text" class="input w-full" />
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">登录安全策略</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">登录错误次数限制</label>
            <input v-model.number="settings.login_error_limit" type="number" min="1" class="input w-full" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">账号锁定时间（分钟）</label>
            <input v-model.number="settings.login_lock_time" type="number" min="1" class="input w-full" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">密码最小长度</label>
            <input v-model.number="settings.password_min_length" type="number" min="6" class="input w-full" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">会话超时时间（分钟）</label>
            <input v-model.number="settings.session_timeout" type="number" min="1" class="input w-full" />
          </div>
          <div class="flex items-center">
            <input v-model="settings.password_require_special" type="checkbox" id="password_require_special" class="mr-2" />
            <label for="password_require_special" class="text-sm text-gray-700">密码需要特殊字符</label>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">文件上传设置</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">文件上传最大大小（MB）</label>
            <input v-model.number="settings.upload_max_size" type="number" min="1" class="input w-full" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">图片上传最大大小（MB）</label>
            <input v-model.number="settings.upload_image_max_size" type="number" min="1" class="input w-full" />
          </div>
          <div class="md:col-span-2">
            <label class="block text-sm font-medium text-gray-700 mb-1">允许上传的文件类型</label>
            <input v-model="settings.upload_allowed_types" type="text" class="input w-full" placeholder="jpg,jpeg,png,gif,pdf" />
          </div>
          <div class="md:col-span-2">
            <label class="block text-sm font-medium text-gray-700 mb-1">允许上传的图片类型</label>
            <input v-model="settings.upload_image_types" type="text" class="input w-full" placeholder="jpg,jpeg,png,gif" />
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">功能开关</h2>
        <div class="space-y-4">
          <div class="flex items-center justify-between py-2 border-b border-gray-100">
            <div>
              <p class="text-sm font-medium text-gray-900">心愿墙功能</p>
              <p class="text-xs text-gray-500">开启后用户可以发布心愿便利贴</p>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input v-model="settings.feature_wish_wall" type="checkbox" class="sr-only peer" />
              <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
            </label>
          </div>
          <div class="flex items-center justify-between py-2 border-b border-gray-100">
            <div>
              <p class="text-sm font-medium text-gray-900">意见征集功能</p>
              <p class="text-xs text-gray-500">开启后用户可以发布意见征集帖子</p>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input v-model="settings.feature_suggestion" type="checkbox" class="sr-only peer" />
              <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
            </label>
          </div>
          <div class="flex items-center justify-between py-2 border-b border-gray-100">
            <div>
              <p class="text-sm font-medium text-gray-900">注册功能</p>
              <p class="text-xs text-gray-500">开启后新用户可以注册账号</p>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input v-model="settings.feature_register" type="checkbox" class="sr-only peer" />
              <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
            </label>
          </div>
          <div class="flex items-center justify-between py-2">
            <div>
              <p class="text-sm font-medium text-gray-900">礼品兑换功能</p>
              <p class="text-xs text-gray-500">开启后学员可以兑换礼品</p>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input v-model="settings.feature_gift_exchange" type="checkbox" class="sr-only peer" />
              <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
            </label>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">SMTP邮箱配置</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">SMTP服务器地址</label>
            <input v-model="settings.smtp_host" type="text" class="input w-full" placeholder="smtp.example.com" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">SMTP端口</label>
            <input v-model.number="settings.smtp_port" type="number" class="input w-full" placeholder="465" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">SMTP用户名</label>
            <input v-model="settings.smtp_user" type="text" class="input w-full" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">SMTP密码</label>
            <input v-model="settings.smtp_password" type="password" class="input w-full" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">发件人邮箱</label>
            <input v-model="settings.smtp_from_email" type="email" class="input w-full" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">发件人名称</label>
            <input v-model="settings.smtp_from_name" type="text" class="input w-full" />
          </div>
          <div class="flex items-center">
            <input v-model="settings.smtp_use_ssl" type="checkbox" id="smtp_use_ssl" class="mr-2" />
            <label for="smtp_use_ssl" class="text-sm text-gray-700">使用SSL</label>
          </div>
        </div>
      </div>

      <div class="flex justify-end gap-4">
        <button @click="fetchSettings" class="btn-secondary">重置</button>
        <button @click="saveSettings" class="btn-primary" :disabled="saving">
          {{ saving ? '保存中...' : '保存设置' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import request from '@/api/request';
import { onMounted, ref } from 'vue';

interface Settings {
  site_name: string;
  site_description: string;
  contact_email: string;
  contact_phone: string;
  login_error_limit: number;
  login_lock_time: number;
  password_min_length: number;
  password_require_special: boolean;
  session_timeout: number;
  upload_max_size: number;
  upload_allowed_types: string;
  upload_image_max_size: number;
  upload_image_types: string;
  feature_wish_wall: boolean;
  feature_suggestion: boolean;
  feature_register: boolean;
  feature_gift_exchange: boolean;
  smtp_host: string;
  smtp_port: number;
  smtp_user: string;
  smtp_password: string;
  smtp_from_email: string;
  smtp_from_name: string;
  smtp_use_ssl: boolean;
}

const settings = ref<Settings>({
  site_name: '',
  site_description: '',
  contact_email: '',
  contact_phone: '',
  login_error_limit: 5,
  login_lock_time: 30,
  password_min_length: 6,
  password_require_special: false,
  session_timeout: 1440,
  upload_max_size: 10,
  upload_allowed_types: '',
  upload_image_max_size: 5,
  upload_image_types: '',
  feature_wish_wall: true,
  feature_suggestion: true,
  feature_register: true,
  feature_gift_exchange: true,
  smtp_host: '',
  smtp_port: 465,
  smtp_user: '',
  smtp_password: '',
  smtp_from_email: '',
  smtp_from_name: '',
  smtp_use_ssl: true,
});

const saving = ref(false);

const fetchSettings = async () => {
  try {
    const data = (await request.get('/api/v1/settings/')) as Record<string, any[]>;
    const allSettings: Record<string, string> = {};
    
    Object.values(data).forEach((categorySettings) => {
      categorySettings.forEach((s: any) => {
        allSettings[s.setting_key] = s.setting_value;
      });
    });

    settings.value = {
      site_name: allSettings.site_name || '',
      site_description: allSettings.site_description || '',
      contact_email: allSettings.contact_email || '',
      contact_phone: allSettings.contact_phone || '',
      login_error_limit: parseInt(allSettings.login_error_limit) || 5,
      login_lock_time: parseInt(allSettings.login_lock_time) || 30,
      password_min_length: parseInt(allSettings.password_min_length) || 6,
      password_require_special: allSettings.password_require_special === 'true',
      session_timeout: parseInt(allSettings.session_timeout) || 1440,
      upload_max_size: parseInt(allSettings.upload_max_size) || 10,
      upload_allowed_types: allSettings.upload_allowed_types || '',
      upload_image_max_size: parseInt(allSettings.upload_image_max_size) || 5,
      upload_image_types: allSettings.upload_image_types || '',
      feature_wish_wall: allSettings.feature_wish_wall !== 'false',
      feature_suggestion: allSettings.feature_suggestion !== 'false',
      feature_register: allSettings.feature_register !== 'false',
      feature_gift_exchange: allSettings.feature_gift_exchange !== 'false',
      smtp_host: allSettings.smtp_host || '',
      smtp_port: parseInt(allSettings.smtp_port) || 465,
      smtp_user: allSettings.smtp_user || '',
      smtp_password: allSettings.smtp_password || '',
      smtp_from_email: allSettings.smtp_from_email || '',
      smtp_from_name: allSettings.smtp_from_name || '',
      smtp_use_ssl: allSettings.smtp_use_ssl !== 'false',
    };
  } catch (error) {
    console.error('获取设置失败:', error);
  }
};

const saveSettings = async () => {
  saving.value = true;
  try {
    const settingsData: Record<string, string> = {
      site_name: settings.value.site_name,
      site_description: settings.value.site_description,
      contact_email: settings.value.contact_email,
      contact_phone: settings.value.contact_phone,
      login_error_limit: String(settings.value.login_error_limit),
      login_lock_time: String(settings.value.login_lock_time),
      password_min_length: String(settings.value.password_min_length),
      password_require_special: String(settings.value.password_require_special),
      session_timeout: String(settings.value.session_timeout),
      upload_max_size: String(settings.value.upload_max_size),
      upload_allowed_types: settings.value.upload_allowed_types,
      upload_image_max_size: String(settings.value.upload_image_max_size),
      upload_image_types: settings.value.upload_image_types,
      feature_wish_wall: String(settings.value.feature_wish_wall),
      feature_suggestion: String(settings.value.feature_suggestion),
      feature_register: String(settings.value.feature_register),
      feature_gift_exchange: String(settings.value.feature_gift_exchange),
      smtp_host: settings.value.smtp_host,
      smtp_port: String(settings.value.smtp_port),
      smtp_user: settings.value.smtp_user,
      smtp_password: settings.value.smtp_password,
      smtp_from_email: settings.value.smtp_from_email,
      smtp_from_name: settings.value.smtp_from_name,
      smtp_use_ssl: String(settings.value.smtp_use_ssl),
    };

    await request.put('/api/v1/settings/', { settings: settingsData });
    alert('设置保存成功');
  } catch (error) {
    console.error('保存设置失败:', error);
    alert('保存设置失败');
  } finally {
    saving.value = false;
  }
};

onMounted(() => {
  fetchSettings();
});
</script>
