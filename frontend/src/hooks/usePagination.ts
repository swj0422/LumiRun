import { ref, computed } from 'vue';

interface PaginationOptions {
  page?: number;
  pageSize?: number;
  total?: number;
  pageSizes?: number[];
}

export function usePagination(options: PaginationOptions = {}) {
  const {
    page = 1,
    pageSize = 20,
    total = 0,
    pageSizes = [10, 20, 50, 100],
  } = options;

  const currentPage = ref(page);
  const currentPageSize = ref(pageSize);
  const totalItems = ref(total);

  const totalPages = computed(() => {
    return Math.ceil(totalItems.value / currentPageSize.value);
  });

  const handlePageChange = (page: number) => {
    if (page >= 1 && page <= totalPages.value) {
      currentPage.value = page;
    }
  };

  const handleSizeChange = (size: number) => {
    currentPageSize.value = size;
    currentPage.value = 1; // 重置到第一页
  };

  const reset = (newTotal?: number) => {
    currentPage.value = 1;
    if (newTotal !== undefined) {
      totalItems.value = newTotal;
    }
  };

  return {
    currentPage,
    currentPageSize,
    totalItems,
    totalPages,
    pageSizes,
    handlePageChange,
    handleSizeChange,
    reset,
  };
}
