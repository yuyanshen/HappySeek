// frontend/src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/crawler'
  },
  {
    path: '/crawler',
    name: 'Crawler',
    component: () => import('@/views/Crawler.vue')
  },
  {
    path: '/tasks',
    name: 'TaskMonitor',
    component: () => import('@/views/TaskMonitor.vue')
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue')
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('@/views/Admin.vue'),
    children: [
      // Admin sub-routes can be added here
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router