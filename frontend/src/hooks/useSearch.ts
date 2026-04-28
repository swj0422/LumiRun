import { ref, watch } from 'vue';
import { debounce } from '@/utils';

interface SearchOptions {
  debounceDelay?: number;
  onSearch?: (keyword: string) => void;
  immediate?: boolean;
}

export function useSearch(options: SearchOptions = {}) {
  const { debounceDelay = 300, onSearch, immediate = false } = options;

  const keyword = ref('');
  const loading = ref(false);

  // 防抖处理的搜索函数
  const debouncedSearch = debounce((searchKeyword: string) => {
    if (onSearch) {
      loading.value = true;
      try {
        onSearch(searchKeyword);
      } finally {
        loading.value = false;
      }
    }
  }, debounceDelay);

  // 监听关键词变化
  watch(keyword, (newKeyword) => {
    debouncedSearch(newKeyword);
  });

  // 立即执行搜索
  if (immediate && keyword.value) {
    debouncedSearch(keyword.value);
  }

  // 手动触发搜索
  const search = (searchKeyword?: string) => {
    const finalKeyword = searchKeyword ?? keyword.value;
    keyword.value = finalKeyword;
    debouncedSearch(finalKeyword);
  };

  // 清空搜索
  const clear = () => {
    keyword.value = '';
    debouncedSearch('');
  };

  return {
    keyword,
    loading,
    search,
    clear,
  };
}
