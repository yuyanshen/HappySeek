import { useMonitoringStore } from '@/stores/modules/monitoring'
import * as Sentry from '@sentry/vue'
import { ElMessage } from 'element-plus'

/**
 * 全局错误处理模块
 * 功能：
 * 1. 控制台错误打印
 * 2. 用户友好提示
 * 3. 认证错误自动跳转
 * 4. 网络错误特殊处理
 * 5. 错误分类上报
 * 6. 错误跟踪和分析
 */

class ErrorHandler {
  constructor() {
    this.monitoringStore = null
    this.initialized = false
  }

  init() {
    if (this.initialized) return

    this.monitoringStore = useMonitoringStore()
    this.initialized = true

    // 添加全局未捕获错误处理
    window.addEventListener('error', this.handleGlobalError.bind(this))
    window.addEventListener('unhandledrejection', this.handlePromiseRejection.bind(this))
  }

  handle(error) {
    console.error('Error caught:', error)

    if (error.response) {
      // HTTP 错误
      this.handleHttpError(error.response)
    } else if (error.request) {
      // 网络错误
      this.handleNetworkError(error)
    } else {
      // 其他错误
      this.handleGenericError(error)
    }
  }

  handleHttpError(response) {
    const status = response.status
    const message = response.data?.message || '未知错误'

    switch (status) {
      case 400:
        ElMessage.error(`请求参数错误: ${message}`)
        break
      case 401:
        ElMessage.error('未授权，请重新登录')
        // 触发登出逻辑
        break
      case 403:
        ElMessage.error('没有权限访问该资源')
        break
      case 404:
        ElMessage.error('请求的资源不存在')
        break
      case 429:
        ElMessage.error('请求过于频繁，请稍后再试')
        break
      case 500:
        ElMessage.error('服务器错误，请稍后重试')
        break
      default:
        ElMessage.error(`请求失败: ${message}`)
    }
  }

  handleNetworkError(error) {
    if (!navigator.onLine) {
      ElMessage.error('网络连接已断开，请检查网络')
    } else {
      ElMessage.error('无法连接到服务器，请稍后重试')
    }
  }

  handleGenericError(error) {
    ElMessage.error(error.message || '发生未知错误')
  }

  handleGlobalError(event) {
    const error = {
      type: 'runtime',
      message: event.message || '未知运行时错误',
      stack: event.error?.stack,
      componentName: this.getComponentName(event),
      routePath: window.location.pathname
    }

    this.logError(error)
  }

  handlePromiseRejection(event) {
    const error = {
      type: 'promise',
      message: event.reason?.message || '未处理的 Promise 拒绝',
      stack: event.reason?.stack,
      routePath: window.location.pathname
    }

    this.logError(error)
  }

  handleVueError(err, vm, info) {
    const error = {
      type: 'vue',
      message: err.message || '未知 Vue 错误',
      stack: err.stack,
      componentName: vm?.$options.name || '未知组件',
      routePath: window.location.pathname,
      info
    }

    this.logError(error)
  }

  handleApiError(error, config) {
    const errorData = {
      type: 'api',
      message: error.message || 'API 请求失败',
      stack: error.stack,
      routePath: window.location.pathname,
      url: config.url,
      method: config.method,
      params: config.params,
      status: error.response?.status
    }

    // 记录慢请求
    if (config.duration > 5000) {
      this.monitoringStore?.markSlowRequest(config.url)
    }

    this.logError(errorData)
  }

  getComponentName(event) {
    const element = event.target
    if (element?.__vueParentComponent) {
      return element.__vueParentComponent.type.name || '未知组件'
    }
    return '未知组件'
  }

  logError(error) {
    if (!this.initialized || !this.monitoringStore) {
      console.error('ErrorHandler 未初始化', error)
      return
    }

    // 添加到监控存储
    this.monitoringStore.addError(error)

    // 开发环境下在控制台显示详细信息
    if (import.meta.env.DEV) {
      console.group('错误详情')
      console.error(error.message)
      console.error('类型:', error.type)
      console.error('组件:', error.componentName)
      console.error('路由:', error.routePath)
      console.error('堆栈:', error.stack)
      console.groupEnd()
    }

    // 发送到 Sentry
    if (import.meta.env.PROD && import.meta.env.VITE_SENTRY_DSN) {
      Sentry.captureException(new Error(error.message), {
        extra: error
      })
    }
  }

  // 用于开发环境的错误分析
  analyzeErrors() {
    if (!this.monitoringStore) return {}

    const errors = this.monitoringStore.errors
    const analysis = {
      totalErrors: errors.length,
      byType: {},
      byComponent: {},
      byRoute: {},
      recentErrors: this.monitoringStore.recentErrors,
      slowRequests: this.monitoringStore.slowRequests
    }

    errors.forEach(error => {
      // 按类型统计
      analysis.byType[error.type] = (analysis.byType[error.type] || 0) + 1

      // 按组件统计
      if (error.componentName) {
        analysis.byComponent[error.componentName] =
          (analysis.byComponent[error.componentName] || 0) + 1
      }

      // 按路由统计
      if (error.routePath) {
        analysis.byRoute[error.routePath] =
          (analysis.byRoute[error.routePath] || 0) + 1
      }
    })

    return analysis
  }
}

export default new ErrorHandler()