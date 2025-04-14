<script setup>
import { onMounted, onUnmounted } from 'vue'
import { useStore } from 'vuex'
import { useRoute } from 'vue-router'
import { setupTaskSocket, disconnectSocket } from '@/utils/socket'
import { ElNotification } from 'element-plus'
import { onMounted } from 'vue'
import errorHandler from '@/utils/errorHandler'

onMounted(() => {
  // 初始化错误监听
  errorHandler.init()
  
  // 测试错误处理（开发环境）
  if (import.meta.env.DEV) {
    window.testError = () => {
      errorHandler.handle(new Error('测试错误'), {
        customTitle: '测试通知'
      })
    }
  }
})

// 状态管理
const store = useStore()
const route = useRoute()

// 初始化WebSocket连接（仅任务页面保持连接）
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

// 初始化操作
onMounted(() => {
  // 1. 初始化必要数据
  store.dispatch('loadAppConfig')
  
  // 2. 设置路由监听管理Socket
  manageSocketConnection()
  
  // 3. 全局错误监听
  window.addEventListener('error', handleError)
  window.addEventListener('unhandledrejection', handleError)
})

// 清理操作
onUnmounted(() => {
  disconnectSocket()
  window.removeEventListener('error', handleError)
  window.removeEventListener('unhandledrejection', handleError)
})

// 路由变化时管理连接
watch(() => route.path, manageSocketConnection)
</script>

<template>
  <el-config-provider namespace="ep">
    <!-- 全局加载状态 -->
    <el-loading 
      v-if="store.state.app.loading" 
      fullscreen 
      lock
      text="系统初始化中..."
    />
    
    <!-- 主内容区 -->
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
    
    <!-- 全局通知容器 -->
    <el-notification-group placement="bottom-right">
      <!-- 内置通知组件将自动注入到这里 -->
    </el-notification-group>
  </el-config-provider>
</template>

<style>
/* 全局过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 修复ElMessage在transition下的层级问题 */
.el-message {
  z-index: 9999 !important;
}
</style>