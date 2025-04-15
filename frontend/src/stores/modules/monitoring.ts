import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

export interface ErrorRecord {
  id: string
  timestamp: number
  type: string
  message: string
  stack?: string
  componentName?: string
  routePath?: string
}

export interface PerformanceRecord {
  timestamp: number
  type: string
  value: number
  route?: string
}

export const useMonitoringStore = defineStore('monitoring', () => {
  // 状态
  const errors = ref<ErrorRecord[]>([])
  const performanceMetrics = ref<PerformanceRecord[]>([])
  const slowRequests = ref<string[]>([])

  // 最大记录数
  const MAX_ERROR_RECORDS = 100
  const MAX_PERFORMANCE_RECORDS = 1000

  // 计算属性
  const errorCount = computed(() => errors.value.length)
  const recentErrors = computed(() =>
    errors.value.slice().sort((a, b) => b.timestamp - a.timestamp).slice(0, 10)
  )

  const averageLoadTime = computed(() => {
    const loadTimes = performanceMetrics.value
      .filter(m => m.type === 'pageLoad')
      .map(m => m.value)

    if (loadTimes.length === 0) return 0
    return loadTimes.reduce((a, b) => a + b, 0) / loadTimes.length
  })

  // 动作
  function addError(error: Omit<ErrorRecord, 'id' | 'timestamp'>) {
    const record: ErrorRecord = {
      id: Math.random().toString(36).substring(2, 9),
      timestamp: Date.now(),
      ...error
    }

    errors.value.push(record)
    if (errors.value.length > MAX_ERROR_RECORDS) {
      errors.value.shift()
    }
  }

  function addPerformanceMetric(metric: Omit<PerformanceRecord, 'timestamp'>) {
    const record: PerformanceRecord = {
      timestamp: Date.now(),
      ...metric
    }

    performanceMetrics.value.push(record)
    if (performanceMetrics.value.length > MAX_PERFORMANCE_RECORDS) {
      performanceMetrics.value.shift()
    }
  }

  function markSlowRequest(url: string) {
    if (!slowRequests.value.includes(url)) {
      slowRequests.value.push(url)
    }
  }

  function clearOldRecords() {
    const oneDayAgo = Date.now() - 24 * 60 * 60 * 1000
    errors.value = errors.value.filter(e => e.timestamp > oneDayAgo)
    performanceMetrics.value = performanceMetrics.value.filter(p => p.timestamp > oneDayAgo)
  }

  // 导出方法和状态
  return {
    // 状态
    errors,
    performanceMetrics,
    slowRequests,

    // 计算属性
    errorCount,
    recentErrors,
    averageLoadTime,

    // 动作
    addError,
    addPerformanceMetric,
    markSlowRequest,
    clearOldRecords
  }
})