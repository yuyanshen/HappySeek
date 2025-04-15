<!-- frontend/src/app.vue -->
<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { Menu } from '@element-plus/icons-vue'
import { setupTaskSocket, disconnectSocket } from '@/utils/socket'
import { useAppStore } from '@/stores/app'
import AppNav from '@/components/AppNav.vue'
import errorHandler from '@/utils/errorHandler'

const appStore = useAppStore()
const route = useRoute()
const isMobile = ref(window.innerWidth < 768)
const isNavVisible = ref(!isMobile.value)

// 页面标题映射
const pageTitles = {
  '/': '仪表盘',
  '/crawler': '爬虫配置',
  '/tasks': '任务监控',
  '/admin/users': '用户管理',
  '/admin/settings': '系统设置',
  '/admin/monitor': '服务监控'
}

const currentPageTitle = computed(() => pageTitles[route.path] || '未知页面')

// 移动端导航切换
const toggleNav = () => {
  isNavVisible.value = !isNavVisible.value
}

// 路由动画钩子
const beforeRouteLeave = (el) => {
  el.style.transform = 'translateX(0)'
  el.style.opacity = '1'
}

const afterRouteEnter = (el) => {
  // 关闭移动端导航
  if (isMobile.value) {
    isNavVisible.value = false
  }
}

// 响应式处理
const handleResize = () => {
  isMobile.value = window.innerWidth < 768
  isNavVisible.value = !isMobile.value
}

// WebSocket 连接管理
const manageSocketConnection = () => {
  if (route.path.startsWith('/tasks')) {
    setupTaskSocket()
  } else {
    disconnectSocket()
  }
}

// 全局错误处理
const handleError = (error) => {
  console.error('Global error:', error)
  ElNotification({
    title: '系统错误',
    message: error.message || '未知错误',
    type: 'error',
    duration: 5000
  })
}

onMounted(() => {
  appStore.loadAppConfig()
  manageSocketConnection()
  window.addEventListener('resize', handleResize)
  window.addEventListener('error', handleError)
  window.addEventListener('unhandledrejection', handleError)
  errorHandler.init()
})

onUnmounted(() => {
  disconnectSocket()
  window.removeEventListener('resize', handleResize)
  window.removeEventListener('error', handleError)
  window.removeEventListener('unhandledrejection', handleError)
})

watch(() => route.path, manageSocketConnection)
</script>
<template>
  <el-config-provider namespace="ep">
    <!-- 深色主题容器 -->
    <div class="app-container" :class="{ 'nav-expanded': !isMobile || isNavVisible }">
      <!-- 导航组件 -->
      <AppNav />
      
      <!-- 移动端导航背景遮罩 -->
      <div 
        v-if="isMobile && isNavVisible" 
        class="nav-backdrop"
        @click="toggleNav"
      ></div>

      <!-- 主内容区域 -->
      <main class="main-content">
        <div class="mobile-header" v-if="isMobile">
          <el-button class="nav-toggle" :icon="Menu" @click="toggleNav" />
          <h1 class="page-title">{{ currentPageTitle }}</h1>
        </div>

        <router-view v-slot="{ Component }">
          <transition 
            name="fade-slide" 
            mode="out-in"
            @before-leave="beforeRouteLeave"
            @enter="afterRouteEnter"
          >
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>

    <!-- 全局加载状态 -->
    <el-loading 
      v-if="appStore.loading" 
      fullscreen 
      lock
      text="系统初始化中..."
    />
    
    <!-- 全局通知容器 -->
    <el-notification-group placement="bottom-right" />
  </el-config-provider>
</template>

<style>
:root {
  color-scheme: dark;
}

.app-container {
  min-height: 100vh;
  background: var(--background-color);
  transition: padding-left var(--transition-normal);
}

.nav-expanded {
  padding-left: 240px;
}

.main-content {
  max-width: 1440px;
  margin: 0 auto;
  padding: 40px;
  min-height: 100vh;
}

.mobile-header {
  position: sticky;
  top: 0;
  z-index: var(--z-index-sticky);
  background: var(--surface-color);
  padding: 16px;
  margin: -40px -40px 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.page-title {
  margin: 0;
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  background: linear-gradient(135deg, var(--primary-color), #5ac8fa);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* 路由过渡动画 */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: opacity var(--transition-normal),
              transform var(--transition-normal);
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .app-container {
    padding-left: 0 !important;
  }

  .main-content {
    padding: 20px;
  }

  .mobile-header {
    margin: -20px -20px 20px;
  }
}

/* 暗色主题增强 */
::selection {
  background: var(--primary-color);
  color: white;
}

/* 滚动条美化 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: var(--border-radius-full);
  transition: background var(--transition-fast);
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* Element Plus 深色主题优化 */
.el-button {
  transition: all var(--transition-fast);
}

.el-button:not(.is-text):not(.is-link):hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.el-menu {
  --el-menu-hover-bg-color: rgba(255, 255, 255, 0.05);
  --el-menu-active-color: var(--primary-color);
}

.el-menu-item.is-active {
  background: rgba(255, 255, 255, 0.05);
  font-weight: var(--font-weight-medium);
}

.el-card,
.el-dialog,
.el-message,
.el-notification {
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
}
</style>