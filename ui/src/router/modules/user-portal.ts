import type { RouteRecordRaw } from 'vue-router'
import { Role } from '@/utils/permission/type'

const userPortalRouter: RouteRecordRaw = {
  path: '/user-portal',
  name: 'UserPortal',
  meta: {
    title: '用户门户',
    icon: 'app-home',
    order: 0,
    // 隐藏路由，不在侧边栏显示
    hidden: true
  },
  redirect: '/user-home',
  component: () => import('@/layout/layout-template/UserLayout.vue'),
  children: [
    {
      path: '/user-home',
      name: 'UserHome',
      meta: {
        title: '首页',
        icon: 'app-home',
        activeMenu: '/user-home'
      },
      component: () => import('@/views/user-home/index.vue')
    },
    {
      path: '/user-knowledge',
      name: 'UserKnowledge',
      meta: {
        title: '知识库',
        icon: 'app-dataset',
        activeMenu: '/user-knowledge'
      },
      component: () => import('@/views/user-knowledge/index.vue')
    }
    // {
    //   path: '/user-ai-apps',
    //   name: 'UserAiApps',
    //   meta: {
    //     title: 'AI应用',
    //     icon: 'app-application',
    //     activeMenu: '/user-ai-apps'
    //   },
    //   component: () => import('@/views/user-ai-apps/index.vue')
    // }
  ]
}

export default userPortalRouter
