const homeRouter = {
  path: '/home',
  name: 'home',
  meta: { title: 'views.home.title', icon: 'app-home', order: 0 },
  redirect: '/home',
  component: () => import('@/layout/layout-template/AppLayout.vue'),
  children: [
    {
      path: '/home',
      name: 'home-index',
      meta: { title: '首页', activeMenu: '/home' },
      component: () => import('@/views/home/index.vue')
    }
  ]
}

export default homeRouter