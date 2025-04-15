import { BrowserTracing } from '@sentry/tracing'
import * as Sentry from '@sentry/vue'
import { debounce } from 'lodash-es'
import { App } from 'vue'
import { Router } from 'vue-router'

interface PerformanceMetrics {
  fcp: number // First Contentful Paint
  lcp: number // Largest Contentful Paint
  fid: number // First Input Delay
  cls: number // Cumulative Layout Shift
  ttfb: number // Time to First Byte
}

export function initMonitoring(app: App, router: Router) {
  // 初始化 Sentry
  if (import.meta.env.VITE_SENTRY_DSN) {
    Sentry.init({
      app,
      dsn: import.meta.env.VITE_SENTRY_DSN,
      integrations: [
        new BrowserTracing({
          routingInstrumentation: Sentry.vueRouterInstrumentation(router),
          tracePropagationTargets: ['localhost', 'api.happyseek.com']
        })
      ],
      tracesSampleRate: import.meta.env.DEV ? 1.0 : 0.1,
      environment: import.meta.env.MODE,
      beforeSend(event) {
        if (import.meta.env.DEV) {
          return null
        }
        return event
      }
    })
  }

  // Web Vitals 监控
  const reportWebVitals = debounce((metrics: PerformanceMetrics) => {
    // 可以将指标发送到自定义分析服务
    console.log('Performance Metrics:', metrics)
  }, 1000)

  // 监听性能指标
  if ('PerformanceObserver' in window) {
    // FCP监控
    const fcpObserver = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.name === 'first-contentful-paint') {
          reportWebVitals({ ...metrics, fcp: entry.startTime })
        }
      }
    })
    fcpObserver.observe({ entryTypes: ['paint'] })

    // LCP监控
    const lcpObserver = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.entryType === 'largest-contentful-paint') {
          reportWebVitals({ ...metrics, lcp: entry.startTime })
        }
      }
    })
    lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] })

    // FID监控
    const fidObserver = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.entryType === 'first-input') {
          reportWebVitals({ ...metrics, fid: entry.processingStart - entry.startTime })
        }
      }
    })
    fidObserver.observe({ entryTypes: ['first-input'] })

    // CLS监控
    let clsValue = 0
    const clsObserver = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (!entry.hadRecentInput) {
          clsValue += entry.value
          reportWebVitals({ ...metrics, cls: clsValue })
        }
      }
    })
    clsObserver.observe({ entryTypes: ['layout-shift'] })

    // TTFB监控
    const ttfbObserver = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.entryType === 'navigation') {
          reportWebVitals({ ...metrics, ttfb: entry.responseStart - entry.requestStart })
        }
      }
    })
    ttfbObserver.observe({ entryTypes: ['navigation'] })
  }

  // 错误监控
  window.addEventListener('error', (event) => {
    Sentry.captureException(event.error)
  })

  window.addEventListener('unhandledrejection', (event) => {
    Sentry.captureException(event.reason)
  })

  // 路由变化监控
  router.beforeEach((to) => {
    Sentry.configureScope((scope) => {
      scope.setTag('route', to.path)
    })
  })
}

// 初始化性能指标对象
const metrics: PerformanceMetrics = {
  fcp: 0,
  lcp: 0,
  fid: 0,
  cls: 0,
  ttfb: 0
}

// 自定义性能监控API
export const performance = {
  mark(name: string) {
    if (window.performance && window.performance.mark) {
      window.performance.mark(name)
    }
  },

  measure(name: string, startMark: string, endMark: string) {
    if (window.performance && window.performance.measure) {
      try {
        window.performance.measure(name, startMark, endMark)
      } catch (e) {
        console.error('Performance measurement error:', e)
      }
    }
  },

  // 获取当前性能指标
  getMetrics(): PerformanceMetrics {
    return { ...metrics }
  }
}