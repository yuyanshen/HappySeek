// frontend/src/router/index.js
import { useMonitoringStore } from '@/stores/modules/monitoring'
import nprogress from 'nprogress'
import 'nprogress/nprogress.css'
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/dashboard'
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/Login.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/dashboard',
      name: 'Dashboard',
      component: () => import('@/views/Dashboard.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/admin',
      name: 'Admin',
      component: () => import('@/views/Admin.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
      children: [
        {
          path: 'monitor',
          name: 'ServiceMonitor',
          component: () => import('@/views/admin/ServiceMonitor.vue'),
          meta: { requiresAuth: true, requiresAdmin: true }
        },
        {
          path: 'settings',
          name: 'Settings',
          component: () => import('@/views/admin/Settings.vue'),
          meta: { requiresAuth: true, requiresAdmin: true }
        },
        {
          path: 'users',
          name: 'Users',
          component: () => import('@/views/admin/Users.vue'),
          meta: { requiresAuth: true, requiresAdmin: true }
        }
      ]
    },
    {
      path: '/crawler',
      name: 'Crawler',
      component: () => import('@/views/Crawler.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/task-monitor',
      name: 'TaskMonitor',
      component: () => import('@/views/TaskMonitor.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/crawler-task/:id',
      name: 'CrawlerTask',
      component: () => import('@/views/CrawlerTask.vue'),
      meta: { requiresAuth: true },
      props: true
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: () => import('@/views/NotFound.vue')
    }
  ]
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 开始加载进度条
  nprogress.start()

  // 监控路由变化
  const monitoringStore = useMonitoringStore()
  const startTime = performance.now()

  // 记录路由性能
  router.afterEach(() => {
    const duration = performance.now() - startTime
    monitoringStore.addPerformanceMetric({
      type: 'routeChange',
      value: duration,
      route: to.fullPath
    })
  })

  // 权限检查
  const token = localStorage.getItem('token')
  const userRole = localStorage.getItem('userRole')

  if (to.meta.requiresAuth && !token) {
    next('/login')
    return
  }

  if (to.meta.requiresAdmin && userRole !== 'admin') {
    next('/dashboard')
    return
  }

  next()
})

// 路由后置守卫
router.afterEach(() => {
  // 结束加载进度条
  nprogress.done()
})

// 路由错误处理
router.onError((error) => {
  nprogress.done()
  const monitoringStore = useMonitoringStore()
  monitoringStore.addError({
    type: 'router',
    message: error.message,
    stack: error.stack
  })
})

export default router