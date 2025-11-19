import { hasPermission } from '@/utils/permission/index'
import NProgress from 'nprogress'
import {
  createRouter,
  createWebHistory,
  type NavigationGuardNext,
  type RouteLocationNormalized,
  type RouteRecordRaw,
  type RouteRecordName
} from 'vue-router'
import useStore from '@/stores'
import { routes } from '@/router/routes'
NProgress.configure({ showSpinner: false, speed: 500, minimum: 0.3 })
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: routes
})

// 路由前置拦截器
router.beforeEach(
  async (to: RouteLocationNormalized, from: RouteLocationNormalized, next: NavigationGuardNext) => {
    NProgress.start()
    if (to.name === '404') {
      next()
      return
    }
    const { user } = useStore()
    const notAuthRouteNameList = ["oauth_login", "oauth-callback", 'register', 'login', 'forgot_password', 'reset_password', 'Chat']
    if (!notAuthRouteNameList.includes(to.name ? to.name.toString() : '')) {
      if (to.query && to.query.token) {
        localStorage.setItem('token', to.query.token.toString())
        //移除 token 参数并重定向（不刷新页面）
        const newQuery = { ...to.query }
        delete newQuery.token
        next({
          path: to.path,
          query: newQuery,
          replace: true
        })
        return

      }
      const token = user.getToken()
      if (!token) {
        next({
          path: '/login'
        })
        return
      }
      if (!user.userInfo) {
        await user.profile()
      }
      
      // 用户角色路由控制
      const userRole = user.userInfo?.role
      const isUserRoute = to.path.startsWith('/user-')
      const isAdminRoute = !isUserRoute && !['/login', '/register', '/forgot_password', '/reset_password', '/oauth_login', '/chat', '/404'].some(path => to.path.startsWith(path))
      
      // 非ADMIN用户只能访问用户页面
      if (userRole !== 'ADMIN' && isAdminRoute) {
        next('/user-home')
        return
      }
      
      // ADMIN用户不应该访问用户专用页面
      if (userRole === 'ADMIN' && isUserRoute) {
        next('/home')
        return
      }
    }
    
    // 判断是否有菜单权限
    if (to.meta.permission ? hasPermission(to.meta.permission as any, 'OR') : true) {
      next()
    } else {
      // 如果没有权限则直接取404页面
      next('404')
    }
  }
)
router.afterEach(() => {
  NProgress.done()
})

export const getChildRouteListByPathAndName = (path: any, name?: RouteRecordName | any) => {
  return getChildRouteList(routes, path, name)
}

export const getChildRouteList: (
  routeList: Array<RouteRecordRaw>,
  path: string,
  name?: RouteRecordName | null | undefined
) => Array<RouteRecordRaw> = (routeList, path, name) => {
  for (let index = 0; index < routeList.length; index++) {
    const route = routeList[index]
    if (name === route.name && path === route.path) {
      return route.children || []
    }
    if (route.children && route.children.length > 0) {
      const result = getChildRouteList(route.children, path, name)
      if (result && result?.length > 0) {
        return result
      }
    }
  }
  return []
}

export default router
