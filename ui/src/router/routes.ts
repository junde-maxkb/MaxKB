import type { RouteRecordRaw } from 'vue-router'
import { Role } from '@/utils/permission/type'

const modules: any = import.meta.glob('./modules/*.ts', { eager: true })
const rolesRoutes: RouteRecordRaw[] = [...Object.keys(modules).map((key) => modules[key].default)]
  .sort((a, b) => {
    const orderA = a.meta?.order ?? 999
    const orderB = b.meta?.order ?? 999
    return orderA - orderB
  })

export const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'root',
    redirect: (to) => {
      // 动态重定向：根据用户角色决定默认页面
      const userStore = JSON.parse(localStorage.getItem('user') || '{}')
      const userRole = userStore.userInfo?.role
      
      if (userRole === 'ADMIN') {
        return '/home'
      } else {
        return '/user-home'
      }
    },
    children: [...rolesRoutes]
  },

  // 高级编排
  {
    path: '/application/:id/workflow',
    name: 'ApplicationWorkflow',
    meta: { activeMenu: '/application' },
    component: () => import('@/views/application-workflow/index.vue')
  },

  {
    path: '/chat/:accessToken',
    name: 'Chat',
    component: () => import('@/views/chat/index.vue')
  },

  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/login/index.vue')
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('@/views/login/register/index.vue')
  },
  {
    path: '/forgot_password',
    name: 'forgot_password',
    component: () => import('@/views/login/forgot-password/index.vue')
  },
  {
    path: '/reset_password/:code/:email',
    name: 'reset_password',
    component: () => import('@/views/login/reset-password/index.vue')
  },
  {
    path: '/:pathMatch(.*)',
    name: '404',
    component: () => import('@/views/404/index.vue')
  },
  {
    path: '/oauth_login',
    name: 'oauth_login',
    component: () => import('@/views/oauth-login/index.vue')
  },
  {
    path: '/oauth-callback',
    name: 'oauth-callback',
    component: () => import('@/views/oauth-callback/index.vue')
  },
  {
    path: '/animation-demo',
    name: 'AnimationDemo',
    component: () => import('@/views/animation-demo/index.vue')
  }
]
