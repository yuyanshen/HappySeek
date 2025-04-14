<!-- frontend/src/app.vue -->
<script setup>
import { onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { setupTaskSocket, disconnectSocket } from '@/utils/socket'
import { ElNotification } from 'element-plus'
import errorHandler from '@/utils/errorHandler'

// Store using Pinia
import { useAppStore } from '@/stores/app'
const appStore = useAppStore()

// Router
const route = useRoute()

// Initialize WebSocket connection (only maintain connection on task pages)
const manageSocketConnection = () => {
  if (route.path.startsWith('/tasks')) {
    setupTaskSocket()
  } else {
    disconnectSocket()
  }
}

// Global error handling
const handleError = (error) => {
  console.error('Global error:', error)
  ElNotification({
    title: '系统错误',
    message: error.message || '未知错误',
    type: 'error',
    duration: 5000
  })
}

// Initialize operations
onMounted(() => {
  // 1. Initialize necessary data
  appStore.loadAppConfig()
  
  // 2. Set up router listener to manage Socket
  manageSocketConnection()
  
  // 3. Global error listener
  window.addEventListener('error', handleError)
  window.addEventListener('unhandledrejection', handleError)
  
  // Initialize error handler
  errorHandler.init()
})

// Cleanup operations
onUnmounted(() => {
  disconnectSocket()
  window.removeEventListener('error', handleError)
  window.removeEventListener('unhandledrejection', handleError)
})

// Watch route changes to manage connection
watch(() => route.path, manageSocketConnection)
</script>
<template>
  <el-config-provider namespace="ep">
    <!-- Global loading status -->
    <el-loading 
      v-if="appStore.loading" 
      fullscreen 
      lock
      text="系统初始化中..."
    />
    
    <!-- Main content area -->
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
    
    <!-- Global notification container -->
    <el-notification-group placement="bottom-right">
      <!-- Built-in notification components will be automatically injected here -->
    </el-notification-group>
  </el-config-provider>
</template>

<style>
/* Global transition animations */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Fix for ElMessage z-index issues under transitions */
.el-message {
  z-index: 9999 !important;
}
</style>