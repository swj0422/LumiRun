/// <reference types="vite/client" />
import { useUserStore } from '@/stores/user';
import { createRouter, createWebHistory } from 'vue-router';
import { getTokenFromCookie } from '@/utils/auth';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login',
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/Login.vue'),
      meta: { public: true },
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('@/views/Register.vue'),
      meta: { public: true },
    },
    {
      path: '/forgot-password',
      name: 'ForgotPassword',
      component: () => import('@/views/ForgotPassword.vue'),
      meta: { public: true },
    },
    {
      path: '/reset-password',
      name: 'ResetPassword',
      component: () => import('@/views/ResetPassword.vue'),
      meta: { public: true },
    },
    {
      path: '/role-selection',
      name: 'RoleSelection',
      component: () => import('@/views/RoleSelection.vue'),
      meta: { public: false },
    },
    // 导师端
    {
      path: '/teacher',
      component: () => import('@/layouts/TeacherLayout.vue'),
      meta: { role: 'teacher' },
      children: [
        {
          path: '',
          name: 'TeacherDashboard',
          component: () => import('@/views/pc/teacher/Dashboard.vue'),
        },
        {
          path: 'classes',
          name: 'TeacherClasses',
          component: () => import('@/views/pc/teacher/ClassList.vue'),
        },
        {
          path: 'classes/:id',
          name: 'TeacherClassDetail',
          component: () => import('@/views/pc/teacher/ClassDetail.vue'),
        },

        {
          path: 'students',
          name: 'TeacherStudents',
          component: () => import('@/views/pc/teacher/StudentList.vue'),
        },
        {
          path: 'growth',
          name: 'TeacherGrowth',
          component: () => import('@/views/pc/teacher/GrowthList.vue'),
        },
        {
          path: 'rewards',
          name: 'TeacherRewards',
          component: () => import('@/views/pc/teacher/RewardList.vue'),
        },
        {
          path: 'orders',
          name: 'TeacherOrders',
          component: () => import('@/views/pc/teacher/OrderList.vue'),
        },
        {
          path: 'tags',
          name: 'TeacherTags',
          component: () => import('@/views/pc/teacher/TagList.vue'),
        },
        {
          path: 'suggestion-forum',
          name: 'TeacherSuggestionForum',
          component: () => import('@/views/pc/teacher/SuggestionForum.vue'),
        },
        {
          path: 'suggestion/:id',
          name: 'TeacherSuggestionDetail',
          component: () => import('@/views/pc/teacher/SuggestionDetail.vue'),
        },
      ],
    },
    // 班级助理端
    {
      path: '/assistant',
      component: () => import('@/layouts/AssistantLayout.vue'),
      meta: { role: 'class_assistant' },
      children: [
        {
          path: '',
          name: 'AssistantHome',
          component: () => import('@/views/pc/assistant/AssistantHome.vue'),
        },
        {
          path: 'students',
          name: 'AssistantStudents',
          component: () => import('@/views/pc/assistant/AssistantStudentList.vue'),
        },
        {
          path: 'growth',
          name: 'AssistantGrowth',
          component: () => import('@/views/pc/assistant/AssistantGrowthRecord.vue'),
        },
        {
          path: 'suggestion-forum',
          name: 'AssistantSuggestionForum',
          component: () => import('@/views/pc/assistant/AssistantSuggestionList.vue'),
        },
        {
          path: 'suggestion/:id',
          name: 'AssistantSuggestionDetail',
          component: () => import('@/views/pc/assistant/AssistantSuggestionDetail.vue'),
        },
      ],
    },
    // 学员端
    {
      path: '/student',
      component: () => import('@/layouts/StudentLayout.vue'),
      meta: { role: 'student' },
      children: [
        {
          path: '',
          name: 'StudentHome',
          component: () => import('@/views/mobile/student/Home.vue'),
        },
        {
          path: 'growth',
          name: 'StudentGrowth',
          component: () => import('@/views/mobile/student/Growth.vue'),
        },
        {
          path: 'shop',
          name: 'StudentShop',
          component: () => import('@/views/mobile/student/Shop.vue'),
        },
        {
          path: 'orders',
          name: 'StudentOrders',
          component: () => import('@/views/mobile/student/OrderList.vue'),
        },
        {
          path: 'rank',
          name: 'StudentRank',
          component: () => import('@/views/mobile/student/Rank.vue'),
        },
        {
          path: 'profile',
          name: 'StudentProfile',
          component: () => import('@/views/mobile/student/Profile.vue'),
        },
        {
          path: 'forum',
          name: 'StudentForum',
          component: () => import('@/views/mobile/student/Forum.vue'),
        },
        {
          path: 'wishes',
          name: 'StudentWishes',
          component: () => import('@/views/mobile/student/WishWall.vue'),
        },
      ],
    },
    // 管理员端
    {
      path: '/admin',
      component: () => import('@/layouts/AdminLayout.vue'),
      meta: { roles: ['admin', 'super_admin'] },
      children: [
        {
          path: '',
          name: 'AdminDashboard',
          component: () => import('@/views/pc/admin/Dashboard.vue'),
        },
        {
          path: 'users',
          name: 'AdminUsers',
          component: () => import('@/views/pc/admin/UserList.vue'),
        },
        {
          path: 'roles',
          name: 'AdminRoles',
          component: () => import('@/views/pc/admin/RoleList.vue'),
        },
        {
          path: 'permissions',
          name: 'AdminPermissions',
          component: () => import('@/views/pc/admin/PermissionList.vue'),
        },
        {
          path: 'logs',
          name: 'AdminLogs',
          component: () => import('@/views/pc/admin/LogList.vue'),
        },
      ],
    },
  ],
});

// 路由守卫
router.beforeEach(async (to, _from, next) => {
  const userStore = useUserStore();

  // 公开页面直接放行
  if (to.meta.public) {
    next();
    return;
  }

  // 检查是否是API请求，API请求不做路由拦截
  if (to.path.startsWith('/api/')) {
    next();
    return;
  }

  // 从Cookie中获取token，确保token值是最新的
  const tokenFromCookie = getTokenFromCookie();

  // 检查是否有token
  if (!tokenFromCookie) {
    next('/login');
    return;
  }

  // 检查是否有用户信息
  if (!userStore.userInfo) {
    try {
      // 先设置token，再获取用户信息
      userStore.setToken(tokenFromCookie);
      await userStore.fetchUserInfo();
    } catch (error) {
      // 不登出用户，保持token，让用户继续尝试
      next();
      return;
    }
  }

  // 检查角色权限
  const userRole = userStore.userInfo?.role_name;
  if (to.meta.role && userRole) {
    // 超级管理员可以访问所有页面
    if (userRole === 'super_admin') {
      next();
      return;
    }
    
    // 检查是否是班级助理（基于student角色的权限）
    const isClassAssistant = localStorage.getItem('isClassAssistant') === 'true';
    const selectedRole = localStorage.getItem('selectedRole');
    
    // 班级助理可以访问助理端页面
    if (userRole === 'student' && isClassAssistant && to.meta.role === 'class_assistant') {
      next();
      return;
    }
    
    // 班级助理可以访问导师端的部分页面
    if (userRole === 'student' && isClassAssistant && to.meta.role === 'teacher') {
      // 班级助理可以访问的页面
      const allowedPaths = [
        '/teacher',
        '/teacher/classes',
        '/teacher/classes/:id',
        '/teacher/students',
        '/teacher/growth',
        '/teacher/suggestion-forum',
        '/teacher/suggestion/:id'
      ];
      
      // 检查当前路径是否在允许的路径列表中
      const isAllowed = allowedPaths.some(path => {
        // 处理带参数的路径
        if (path.includes(':')) {
          const regex = new RegExp('^' + path.replace(/:\w+/g, '[^/]+') + '$');
          return regex.test(to.path);
        }
        return to.path === path;
      });
      
      if (isAllowed) {
        next();
        return;
      } else {
        next('/assistant');
        return;
      }
    }
    
    // 允许班级助理切换到学员身份
    if (userRole === 'student' && to.meta.role === 'student') {
      next();
      return;
    }
    
    // 其他角色权限检查
    if (userRole !== to.meta.role) {
      if (userRole === 'teacher') {
        next('/teacher');
      } else if (userRole === 'student') {
        // 检查是否选择了助理身份
        if (selectedRole === 'class_assistant' && isClassAssistant) {
          next('/assistant');
        } else {
          next('/student');
        }
      } else if (userRole === 'admin') {
        next('/admin');
      } else {
        next('/login');
      }
      return;
    }
  }

  // 检查多角色权限
  if (to.meta.roles && Array.isArray(to.meta.roles) && userRole) {
    // 检查用户角色是否在允许的角色列表中
    const isAllowed = to.meta.roles.includes(userRole);
    if (!isAllowed) {
      if (userRole === 'teacher') {
        next('/teacher');
      } else if (userRole === 'student') {
        next('/student');
      } else if (userRole === 'admin' || userRole === 'super_admin') {
        next('/admin');
      } else {
        next('/login');
      }
      return;
    }
  }

  // 直接放行，让页面自己处理
  next();
});

export default router;
