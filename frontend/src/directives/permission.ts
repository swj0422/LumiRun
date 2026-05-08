import { Directive } from 'vue';
import { userPermissions } from '@/composables/usePermission';

export const permission: Directive = {
  mounted(el, binding) {
    const permissionCode = binding.value;
    
    if (permissionCode && !userPermissions.value.includes(permissionCode)) {
      el.style.display = 'none';
    }
  },
  updated(el, binding) {
    const permissionCode = binding.value;
    
    if (permissionCode && !userPermissions.value.includes(permissionCode)) {
      el.style.display = 'none';
    } else {
      el.style.display = '';
    }
  },
};

export const permissionAny: Directive = {
  mounted(el, binding) {
    const permissionCodes = binding.value;
    
    if (Array.isArray(permissionCodes) && !permissionCodes.some(p => userPermissions.value.includes(p))) {
      el.style.display = 'none';
    }
  },
  updated(el, binding) {
    const permissionCodes = binding.value;
    
    if (Array.isArray(permissionCodes) && !permissionCodes.some(p => userPermissions.value.includes(p))) {
      el.style.display = 'none';
    } else {
      el.style.display = '';
    }
  },
};
