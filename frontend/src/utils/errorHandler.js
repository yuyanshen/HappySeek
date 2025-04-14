import { ElNotification, ElMessageBox } from 'element-plus'
import { useStore } from 'vuex'
import router from '@/router'

/**
 * 全局错误处理模块
 * 功能：
 * 1. 控制台错误打印
 * 2. 用户友好提示
 * 3. 认证错误自动跳转
 * 4. 网络错误特殊处理
 * 5. 错误分类上报
 */

// 错误类型映射
const ERROR_TYPES = {
  NETWORK: {
    code: 1000,
    message: '网络连接异常',
    handler: showNetworkError
  },
  AUTH: {
    code: 401,
    message: '登录已过期',
    handler: handleAuthError
  },
  API: {
    code: 500,
    message: '服务端错误',
    handler: showServiceError
  },
  DEFAULT: {
    code: -1,
    message: '未知错误',
    handler: showDefaultError
  }
}

// 初始化错误监听
export function initErrorHandler() {
  // 1. 全局同步错误
  window.addEventListener('error', (event) => {
    handleError(event.error || new Error(event.message))
  })

  // 2. 全局异步错误
  window.addEventListener('unhandledrejection', (event) => {
    handleError(event.reason)
  })

  // 3. Vue错误
  if (window.Vue?.config) {
    window.Vue.config.errorHandler = handleError
  }
}

// 核心错误处理
export function handleError(error, customConfig = {}) {
  const store = useStore()
  
  // 1. 控制台打印
  console.groupCollapsed('🚨 全局错误捕获')
  console.error('Error:', error)
  console.trace('Stack trace:')
  console.groupEnd()

  // 2. 识别错误类型
  const errorType = identifyErrorType(error)
  
  // 3. 执行对应处理
  errorType.handler(error, {
    ...customConfig,
    store,
    router
  })

  // 4. 错误上报（可选）
  if (process.env.NODE_ENV === 'production') {
    reportError(error)
  }
}

// 错误类型识别
function identifyErrorType(error) {
  if (!error) return ERROR_TYPES.DEFAULT
  
  // 网络错误
  if (error.message?.includes('Network Error')) {
    return ERROR_TYPES.NETWORK
  }
  
  // HTTP状态码错误
  if (error.response) {
    switch (error.response.status) {
      case 401:
        return ERROR_TYPES.AUTH
      case 500:
        return ERROR_TYPES.API
    }
  }
  
  return ERROR_TYPES.DEFAULT
}

/* ---------- 具体错误处理器 ---------- */

// 网络错误处理
function showNetworkError(error, { store }) {
  store.commit('setOfflineMode', true)
  
  ElNotification.error({
    title: '网络中断',
    message: '检测到网络连接异常，请检查网络设置',
    duration: 0, // 不自动关闭
    onClick: () => window.location.reload()
  })
}

// 认证错误处理
function handleAuthError(error, { store, router }) {
  store.dispatch('logout')
  
  ElMessageBox.confirm(
    '登录状态已过期，请重新登录',
    '会话过期',
    {
      confirmButtonText: '重新登录',
      showCancelButton: false,
      closeOnClickModal: false,
      closeOnPressEscape: false
    }
  ).then(() => {
    router.push('/login')
  })
}

// 服务端错误处理
function showServiceError(error) {
  ElNotification.error({
    title: '服务异常',
    message: `服务器处理失败: ${error.response?.data?.message || '未知错误'}`,
    duration: 5000
  })
}

// 默认错误处理
function showDefaultError(error) {
  ElNotification.warning({
    title: '操作异常',
    message: error.message || '未知错误发生',
    duration: 3000
  })
}

// 错误上报（示例）
function reportError(error) {
  const info = {
    time: new Date().toISOString(),
    message: error.message,
    stack: error.stack,
    url: window.location.href,
    userAgent: navigator.userAgent
  }
  
  // 实际项目中替换为您的上报接口
  navigator.sendBeacon?.('/api/error-log', JSON.stringify(info))
}

export default {
  init: initErrorHandler,
  handle: handleError
}