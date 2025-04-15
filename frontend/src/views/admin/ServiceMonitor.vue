<template>
  <div class="service-monitor-view">
    <el-tabs v-model="activeTab">
      <!-- 系统监控 -->
      <el-tab-pane label="系统监控" name="system">
        <service-monitor />
      </el-tab-pane>

      <!-- 健康状态 -->
      <el-tab-pane label="健康状态" name="health">
        <div class="health-status">
          <el-descriptions
            v-if="healthData"
            title="系统健康状态"
            :column="2"
            border
          >
            <template #extra>
              <el-button type="primary" @click="refreshHealth">
                刷新
              </el-button>
            </template>

            <el-descriptions-item label="状态">
              <el-tag :type="healthData.status === 'healthy' ? 'success' : 'danger'">
                {{ healthData.status }}
              </el-tag>
            </el-descriptions-item>

            <el-descriptions-item label="版本">
              {{ healthData.version }}
            </el-descriptions-item>

            <el-descriptions-item label="检查时间">
              {{ formatDate(healthData.timestamp) }}
            </el-descriptions-item>
          </el-descriptions>

          <div v-if="healthData?.components" class="components-status">
            <h3>组件状态</h3>
            <el-card v-for="(component, name) in healthData.components"
                     :key="name"
                     :class="['component-card', component.status]">
              <template #header>
                <div class="component-header">
                  <span>{{ name }}</span>
                  <el-tag :type="getStatusType(component.status)">
                    {{ component.status }}
                  </el-tag>
                </div>
              </template>

              <div v-if="component.message" class="message">
                {{ component.message }}
              </div>

              <div v-if="component.metrics" class="metrics">
                <el-progress
                  v-for="(value, metric) in component.metrics"
                  :key="metric"
                  :percentage="value"
                  :status="getProgressStatus(value)"
                  :format="percentageFormatter"
                >
                  {{ metric }}
                </el-progress>
              </div>
            </el-card>
          </div>
        </div>
      </el-tab-pane>

      <!-- 性能分析 -->
      <el-tab-pane label="性能分析" name="performance">
        <div class="performance-analysis">
          <div class="charts-container">
            <el-row :gutter="20">
              <el-col :span="12">
                <div ref="responseTimeChartRef" class="chart"></div>
              </el-col>
              <el-col :span="12">
                <div ref="requestRateChartRef" class="chart"></div>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <div ref="cpuUsageChartRef" class="chart"></div>
              </el-col>
              <el-col :span="12">
                <div ref="memoryUsageChartRef" class="chart"></div>
              </el-col>
            </el-row>
          </div>
        </div>
      </el-tab-pane>

      <!-- 错误日志 -->
      <el-tab-pane label="错误日志" name="errors">
        <div class="error-analysis">
          <el-table :data="errorStats" stripe>
            <el-table-column prop="timestamp" label="时间" sortable>
              <template #default="{ row }">
                {{ formatDate(row.timestamp) }}
              </template>
            </el-table-column>
            <el-table-column prop="endpoint" label="接口" />
            <el-table-column prop="method" label="方法" width="100" />
            <el-table-column prop="status" label="状态码" width="100">
              <template #default="{ row }">
                <el-tag :type="getHttpStatusType(row.status)">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="count" label="次数" width="100" sortable />
          </el-table>
        </div>
      </el-tab-pane>

      <!-- 原始指标 -->
      <el-tab-pane label="原始指标" name="metrics">
        <div class="raw-metrics">
          <pre>{{ metricsData }}</pre>
        </div>
      </el-tab-pane>

      <!-- 日志分析 -->
      <el-tab-pane label="日志分析" name="logs">
        <div class="log-analysis">
          <el-row :gutter="20" class="filter-row">
            <el-col :span="8">
              <el-select v-model="logTimeRange" placeholder="时间范围">
                <el-option label="最近1小时" value="1" />
                <el-option label="最近24小时" value="24" />
                <el-option label="最近7天" value="168" />
              </el-select>
            </el-col>
            <el-col :span="16" class="text-right">
              <el-button type="primary" @click="exportLogReport">
                导出分析报告
              </el-button>
            </el-col>
          </el-row>

          <!-- 错误统计卡片 -->
          <el-row :gutter="20" class="stats-row">
            <el-col :span="8" v-for="stat in logStats" :key="stat.label">
              <el-card shadow="hover" class="stat-card">
                <div class="stat-value" :class="stat.status">{{ stat.value }}</div>
                <div class="stat-label">{{ stat.label }}</div>
              </el-card>
            </el-col>
          </el-row>

          <!-- 错误趋势图表 -->
          <div class="chart-container">
            <div ref="errorTrendsChartRef" class="chart"></div>
          </div>

          <!-- 错误类型分布 -->
          <el-card class="error-types">
            <template #header>
              <div class="card-header">
                <span>错误类型分布</span>
              </div>
            </template>
            <el-table :data="errorTypes" stripe>
              <el-table-column prop="type" label="错误类型" />
              <el-table-column prop="count" label="数量" width="120" />
              <el-table-column prop="percentage" label="占比" width="120">
                <template #default="{ row }">
                  <el-progress
                    :percentage="row.percentage"
                    :status="getProgressStatus(row.percentage)"
                  />
                </template>
              </el-table-column>
            </el-table>
          </el-card>

          <!-- 最近异常列表 -->
          <el-card class="recent-exceptions">
            <template #header>
              <div class="card-header">
                <span>最近异常</span>
              </div>
            </template>
            <el-table :data="recentExceptions" stripe>
              <el-table-column prop="message" label="异常信息">
                <template #default="{ row }">
                  <el-tooltip
                    effect="dark"
                    :content="row.message"
                    placement="top"
                    :show-after="500"
                  >
                    <span class="truncate">{{ row.message }}</span>
                  </el-tooltip>
                </template>
              </el-table-column>
              <el-table-column prop="count" label="出现次数" width="120" sortable />
              <el-table-column fixed="right" label="操作" width="120">
                <template #default="{ row }">
                  <el-button link @click="showExceptionDetail(row)">
                    详情
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>

          <!-- 慢请求分析 -->
          <el-card class="slow-requests">
            <template #header>
              <div class="card-header">
                <span>慢请求分析</span>
              </div>
            </template>
            <el-table :data="slowRequests" stripe>
              <el-table-column prop="endpoint" label="接口" />
              <el-table-column prop="avgTime" label="平均响应时间" width="160">
                <template #default="{ row }">
                  {{ row.avgTime.toFixed(2) }}ms
                </template>
              </el-table-column>
              <el-table-column prop="maxTime" label="最大响应时间" width="160">
                <template #default="{ row }">
                  {{ row.maxTime.toFixed(2) }}ms
                </template>
              </el-table-column>
              <el-table-column prop="count" label="请求次数" width="120" />
            </el-table>
          </el-card>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'
import dayjs from 'dayjs'
import ServiceMonitor from '@/components/ServiceMonitor.vue'
import { monitoringAPI } from '@/api/monitoring'
import type { HealthCheck, ErrorData, PerformanceData } from '@/api/monitoring'

const activeTab = ref('system')
const healthData = ref<HealthCheck | null>(null)
const errorStats = ref<ErrorData[]>([])
const performanceData = ref<PerformanceData | null>(null)
const metricsData = ref<string>('')

// 日志分析相关状态
const logTimeRange = ref('24')
const logStats = ref([
  { label: '错误总数', value: '0', status: 'normal' },
  { label: '警告数量', value: '0', status: 'warning' },
  { label: '严重错误', value: '0', status: 'danger' }
])
const errorTypes = ref([])
const recentExceptions = ref([])
const slowRequests = ref([])

// 图表实例
let responseTimeChart: echarts.ECharts | null = null
let requestRateChart: echarts.ECharts | null = null
let cpuUsageChart: echarts.ECharts | null = null
let memoryUsageChart: echarts.ECharts | null = null
let errorTrendsChart: echarts.ECharts | null = null

// 自动刷新定时器
let refreshTimer: number | null = null

// 格式化日期
const formatDate = (date: string) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

// 获取状态类型
const getStatusType = (status: string) => {
  switch (status) {
    case 'healthy':
      return 'success'
    case 'warning':
      return 'warning'
    case 'unhealthy':
      return 'danger'
    default:
      return 'info'
  }
}

// 获取HTTP状态码类型
const getHttpStatusType = (status: string) => {
  const code = parseInt(status)
  if (code < 400) return 'success'
  if (code < 500) return 'warning'
  return 'danger'
}

// 获取进度条状态
const getProgressStatus = (value: number) => {
  if (value > 90) return 'exception'
  if (value > 70) return 'warning'
  return 'success'
}

// 格式化百分比
const percentageFormatter = (val: number) => {
  return `${val}%`
}

// 初始化图表
const initCharts = () => {
  // 响应时间图表
  responseTimeChart = echarts.init(document.querySelector('.chart') as HTMLElement)
  responseTimeChart.setOption({
    title: { text: '响应时间分布' },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'time' },
    yAxis: { type: 'value', name: '响应时间(ms)' },
    series: [{
      name: '响应时间',
      type: 'line',
      smooth: true,
      data: []
    }]
  })

  // 请求率图表
  requestRateChart = echarts.init(document.querySelectorAll('.chart')[1] as HTMLElement)
  requestRateChart.setOption({
    title: { text: '请求率趋势' },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'time' },
    yAxis: { type: 'value', name: '请求数/分钟' },
    series: [{
      name: '请求率',
      type: 'line',
      smooth: true,
      data: []
    }]
  })

  // CPU使用率图表
  cpuUsageChart = echarts.init(document.querySelectorAll('.chart')[2] as HTMLElement)
  cpuUsageChart.setOption({
    title: { text: 'CPU使用率' },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: [] },
    yAxis: { type: 'value', name: 'CPU使用率(%)' },
    series: [{
      name: 'CPU',
      type: 'line',
      data: []
    }]
  })

  // 内存使用率图表
  memoryUsageChart = echarts.init(document.querySelectorAll('.chart')[3] as HTMLElement)
  memoryUsageChart.setOption({
    title: { text: '内存使用率' },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: [] },
    yAxis: { type: 'value', name: '内存使用率(%)' },
    series: [{
      name: '内存',
      type: 'line',
      data: []
    }]
  })

  // 错误趋势图表
  errorTrendsChart = echarts.init(document.querySelector('.error-trends-chart') as HTMLElement)
  errorTrendsChart.setOption({
    title: { text: '错误趋势' },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    legend: {
      data: ['错误', '警告', '严重错误']
    },
    xAxis: {
      type: 'category',
      data: []
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '错误',
        type: 'bar',
        stack: 'total',
        data: []
      },
      {
        name: '警告',
        type: 'bar',
        stack: 'total',
        data: []
      },
      {
        name: '严重错误',
        type: 'bar',
        stack: 'total',
        data: []
      }
    ]
  })

  // 窗口大小调整时重绘图表
  window.addEventListener('resize', () => {
    responseTimeChart?.resize()
    requestRateChart?.resize()
    cpuUsageChart?.resize()
    memoryUsageChart?.resize()
    errorTrendsChart?.resize()
  })
}

// 更新图表数据
const updateCharts = () => {
  if (!performanceData.value) return

  // 更新响应时间图表
  responseTimeChart?.setOption({
    series: [{
      data: performanceData.value.response_times.map(item => [
        item.timestamp,
        item.value
      ])
    }]
  })

  // 更新请求率图表
  requestRateChart?.setOption({
    series: [{
      data: performanceData.value.request_rates.map(item => [
        item.timestamp,
        item.value
      ])
    }]
  })

  // 更新资源使用图表
  const timePoints = Array.from({ length: 60 }, (_, i) => i + 1)

  cpuUsageChart?.setOption({
    xAxis: { data: timePoints },
    series: [{
      data: performanceData.value.resources.cpu
    }]
  })

  memoryUsageChart?.setOption({
    xAxis: { data: timePoints },
    series: [{
      data: performanceData.value.resources.memory
    }]
  })
}

// 更新错误趋势图表
const updateErrorTrendsChart = (trends: any) => {
  const dates = Object.keys(trends)
  const errors = dates.map(date => trends[date].errors || 0)
  const warnings = dates.map(date => trends[date].warnings || 0)
  const criticals = dates.map(date => trends[date].critical || 0)

  errorTrendsChart?.setOption({
    xAxis: {
      data: dates
    },
    series: [
      { data: errors },
      { data: warnings },
      { data: criticals }
    ]
  })
}

// 加载日志分析数据
const loadLogAnalysis = async () => {
  try {
    const [analysis, trends] = await Promise.all([
      monitoringAPI.getLogAnalysis(Number(logTimeRange.value)),
      monitoringAPI.getLogTrends()
    ])

    // 更新统计数据
    logStats.value[0].value = analysis.error_count.toString()
    logStats.value[1].value = analysis.warning_count.toString()
    logStats.value[2].value = analysis.critical_count.toString()

    // 更新错误类型
    const totalErrors = analysis.error_count || 1
    errorTypes.value = Object.entries(analysis.errors_by_type).map(([type, count]) => ({
      type,
      count,
      percentage: Math.round((count as number / totalErrors) * 100)
    }))

    // 更新最近异常
    recentExceptions.value = analysis.recent_exceptions

    // 更新错误趋势图表
    updateErrorTrendsChart(trends)

    // 更新慢请求数据
    const performanceData = await monitoringAPI.getPerformanceStats()
    slowRequests.value = Object.entries(performanceData.log_analysis.slow_endpoints)
      .map(([endpoint, time]) => ({
        endpoint,
        avgTime: time,
        maxTime: time * 1.5, // 估算值
        count: performanceData.log_analysis.request_rates[endpoint] || 0
      }))
      .sort((a, b) => b.avgTime - a.avgTime)

  } catch (error) {
    console.error('Failed to load log analysis:', error)
  }
}

// 导出日志报告
const exportLogReport = async () => {
  try {
    const response = await monitoringAPI.exportLogAnalysis()
    if (response.status === 'success') {
      ElMessage.success('报告导出成功')
    } else {
      ElMessage.error(response.message || '报告导出失败')
    }
  } catch (error) {
    console.error('Failed to export log report:', error)
    ElMessage.error('报告导出失败')
  }
}

// 显示异常详情
const showExceptionDetail = (exception: any) => {
  ElMessageBox.alert(exception.message, '异常详情', {
    confirmButtonText: '确定',
    customClass: 'exception-detail-dialog'
  })
}

// 刷新数据
const refreshData = async () => {
  try {
    const [health, errors, performance, metrics] = await Promise.all([
      monitoringAPI.getDetailedHealth(),
      monitoringAPI.getErrorStats(),
      monitoringAPI.getPerformanceStats(),
      monitoringAPI.getMetrics()
    ])

    healthData.value = health
    errorStats.value = errors
    performanceData.value = performance
    metricsData.value = metrics

    updateCharts()
    await loadLogAnalysis()
  } catch (error) {
    console.error('Failed to refresh monitoring data:', error)
  }
}

// 刷新健康状态
const refreshHealth = () => {
  monitoringAPI.getDetailedHealth()
    .then(data => {
      healthData.value = data
    })
    .catch(error => {
      console.error('Failed to refresh health status:', error)
    })
}

// 开始自动刷新
const startAutoRefresh = () => {
  refreshTimer = window.setInterval(refreshData, 30000) // 每30秒刷新一次
}

// 监听时间范围变化
watch(logTimeRange, () => {
  loadLogAnalysis()
})

// 组件挂载
onMounted(() => {
  initCharts()
  refreshData()
  startAutoRefresh()
})

// 组件卸载
onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
  responseTimeChart?.dispose()
  requestRateChart?.dispose()
  cpuUsageChart?.dispose()
  memoryUsageChart?.dispose()
  errorTrendsChart?.dispose()
})
</script>

<style scoped lang="scss">
.service-monitor-view {
  padding: 20px;

  .health-status {
    margin-top: 20px;

    .components-status {
      margin-top: 20px;

      h3 {
        margin-bottom: 15px;
      }

      .component-card {
        margin-bottom: 15px;

        &.healthy {
          border-color: #67C23A;
        }

        &.warning {
          border-color: #E6A23C;
        }

        &.unhealthy {
          border-color: #F56C6C;
        }

        .component-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .message {
          margin-bottom: 10px;
          color: #606266;
        }

        .metrics {
          .el-progress {
            margin-bottom: 10px;
          }
        }
      }
    }
  }

  .performance-analysis {
    .charts-container {
      .chart {
        height: 300px;
        margin-bottom: 20px;
      }
    }
  }

  .error-analysis {
    margin-top: 20px;
  }

  .raw-metrics {
    margin-top: 20px;

    pre {
      padding: 15px;
      background-color: #f8f9fa;
      border-radius: 4px;
      font-family: monospace;
      white-space: pre-wrap;
    }
  }

  .log-analysis {
    .filter-row {
      margin-bottom: 20px;
    }

    .text-right {
      text-align: right;
    }

    .stats-row {
      margin-bottom: 20px;
    }

    .chart-container {
      margin-bottom: 20px;
      height: 300px;

      .chart {
        width: 100%;
        height: 100%;
      }
    }

    .error-types,
    .recent-exceptions,
    .slow-requests {
      margin-bottom: 20px;
    }

    .truncate {
      display: inline-block;
      max-width: 400px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
  }

  .exception-detail-dialog {
    .el-message-box__message {
      white-space: pre-wrap;
      font-family: monospace;
    }
  }
}
</style>