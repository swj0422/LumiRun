<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 顶部导航 -->
    <div class="bg-white shadow-sm">
      <div class="max-w-md mx-auto px-4 py-3 flex items-center justify-between">
        <button @click="goBack" class="w-8 h-8 flex items-center justify-center">
          <svg class="w-6 h-6 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <h1 class="text-lg font-semibold text-gray-800">心愿墙</h1>
        <div class="w-8"></div>
      </div>
    </div>

    <!-- 可用成长值提示 -->
    <div class="px-4 py-4 bg-gradient-to-r from-primary-500 to-primary-600">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-white text-sm opacity-80">可用成长值</p>
          <p class="text-white text-2xl font-bold">{{ growthScore.available_score }}</p>
        </div>
        <router-link to="/student/shop" class="bg-white text-primary-600 px-4 py-2 rounded-lg text-sm font-medium">
          去兑换
        </router-link>
      </div>
    </div>

    <!-- 心愿列表 -->
    <div class="px-4 py-4">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">我的心愿</h2>
      
      <div v-if="myWishes.length > 0" class="space-y-3">
        <div
          v-for="wish in myWishes"
          :key="wish.id"
          class="card p-4"
        >
          <div class="flex items-start space-x-3">
            <img
              :src="wish.gift_image_url || '/api/placeholder-image'"
              :alt="wish.gift_name"
              class="w-16 h-16 rounded-lg object-cover flex-shrink-0"
            />
            <div class="flex-1">
              <div class="flex justify-between items-start">
                <h3 class="font-medium text-gray-800">{{ wish.gift_name }}</h3>
                <button @click="removeWish(wish.id)" class="text-gray-400 hover:text-danger-500">
                  <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <p class="text-sm text-gray-500 mt-1">{{ wish.price }} 成长值</p>
              <div class="mt-2 flex items-center">
                <span 
                  :class="{
                    'px-2 py-0.5 rounded-full text-xs': true,
                    'bg-success-100 text-success-800': wish.status === 'completed',
                    'bg-primary-100 text-primary-800': wish.status === 'pending'
                  }"
                >
                  {{ wish.status === 'completed' ? '已实现' : '进行中' }}
                </span>
                <span v-if="wish.status === 'pending'" class="ml-2 text-xs text-gray-500">
                  还差 {{ wish.price - growthScore.available_score }} 成长值
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="card p-8 text-center">
        <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg class="w-8 h-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        </div>
        <p class="text-gray-500">暂无心愿</p>
        <p class="text-sm text-gray-400 mt-1">去礼品商店挑选心仪的礼品吧</p>
        <router-link to="/student/shop" class="inline-block mt-4 btn-primary text-sm px-6 py-2">
          去逛逛
        </router-link>
      </div>
    </div>

    <!-- 推荐礼品 -->
    <div class="px-4 py-4">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">推荐礼品</h2>
      
      <div v-if="recommendGifts.length > 0" class="grid grid-cols-2 gap-4">
        <div
          v-for="gift in recommendGifts"
          :key="gift.id"
          class="card p-3"
        >
          <img
            :src="gift.image_url || '/api/placeholder-image'"
            :alt="gift.name"
            class="w-full aspect-square rounded-lg object-cover mb-3"
          />
          <h3 class="text-sm font-medium text-gray-800 truncate">{{ gift.name }}</h3>
          <div class="flex items-center justify-between mt-2">
            <span class="text-primary-600 font-semibold">{{ gift.price }} 成长值</span>
            <button
              @click="addWish(gift)"
              class="text-xs px-3 py-1 rounded-full border border-primary-500 text-primary-500 hover:bg-primary-50"
            >
              {{ hasWish(gift.id) ? '已添加' : '心愿单' }}
            </button>
          </div>
        </div>
      </div>

      <div v-else class="card p-6 text-center">
        <p class="text-gray-500">暂无推荐礼品</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import request from '@/api/request';
import { ref, onMounted } from 'vue';

const growthScore = ref({
  total_score: 0,
  available_score: 0,
});

const myWishes = ref<any[]>([]);
const recommendGifts = ref<any[]>([]);

// 返回上一页
const goBack = () => {
  window.history.back();
};

// 获取成长值
const fetchGrowthScore = async () => {
  try {
    const response = await request.get('/api/v1/growth/score');
    if (response) {
      growthScore.value = {
        total_score: response.total_score,
        available_score: response.available_score,
      };
    }
  } catch (error) {
    console.error('获取成长值失败:', error);
  }
};

// 获取我的心愿
const fetchMyWishes = async () => {
  try {
    const response = await request.get('/api/v1/wishes/my');
    if (response && response.items) {
      myWishes.value = response.items;
    }
  } catch (error) {
    console.error('获取我的心愿失败:', error);
  }
};

// 获取推荐礼品
const fetchRecommendGifts = async () => {
  try {
    const response = await request.get('/api/v1/gifts');
    if (response && response.items) {
      recommendGifts.value = response.items.slice(0, 6);
    }
  } catch (error) {
    console.error('获取推荐礼品失败:', error);
  }
};

// 添加心愿
const addWish = async (gift: any) => {
  if (hasWish(gift.id)) {
    return;
  }

  try {
    const response = await request.post('/api/v1/wishes', {
      gift_id: gift.id,
    });
    if (response.message === '添加成功') {
      await fetchMyWishes();
    }
  } catch (error) {
    console.error('添加心愿失败:', error);
  }
};

// 移除心愿
const removeWish = async (wishId: number) => {
  try {
    await request.delete(`/api/v1/wishes/${wishId}`);
    await fetchMyWishes();
  } catch (error) {
    console.error('移除心愿失败:', error);
  }
};

// 判断是否已添加心愿
const hasWish = (giftId: number): boolean => {
  return myWishes.value.some(wish => wish.gift_id === giftId);
};

onMounted(async () => {
  await fetchGrowthScore();
  await fetchMyWishes();
  await fetchRecommendGifts();
});
</script>