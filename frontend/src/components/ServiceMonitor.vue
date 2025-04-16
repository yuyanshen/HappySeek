<template>
  <div class="service-monitor">
    <el-card class="monitor-card">
      <template #header>
        <div class="card-header">
          <span>系统监控面板</span>
          <el-button-group>
            <el-button size="small" @click="refresh">刷新</el-button>
            <el-button size="small" type="primary" @click="toggleAutoRefresh">
              {{ autoRefresh ? '停止自动刷新' : '开始自动刷新' }}
            </el-button>
          </el-button-group>
        </div>
      </template>

      <!-- 系统概览 -->
      <el-row :gutter="20" class="stats-row">
        <el-col :span="6" v-for="stat in systemStats" :key="stat.label">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-value" :class="stat.status">{{ stat.value }}</div>
            <div class="stat-label">{{ stat.label }}</div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 性能指标图表 -->
      <div class="charts-container">
        <div class="chart-wrapper">
          <div ref="responseTimeChart" class="chart"></div>
        </div>
        <div class="chart-wrapper">
          <div ref="requestRateChart" class="chart"></div>
        </div>
      </div>

      <!-- 错误日志表格 -->
      <div class="error-logs">
        <h3>最近错误日志</h3>
        <el-table :data="errorLogs" stripe>
          <el-table-column prop="timestamp" label="时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.timestamp) }}
            </template>
          </el-table-column>
          <el-table-column prop="type" label="类型" width="120" />
          <el-table-column prop="message" label="错误信息" />
          <el-table-column fixed="right" label="操作" width="120">
            <template #default="{ row }">
              <el-button link @click="showErrorDetail(row)">详情</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>

    <!-- 错误详情对话框 -->
    <el-dialog
      v-model="errorDetailVisible"
      title="错误详情"
      width="60%"
    >
      <div v-if="selectedError">
        <el-descriptions border>
          <el-descriptions-item label="错误类型">{{ selectedError.type }}</el-descriptions-item>
          <el-descriptions-item label="发生时间">{{ formatDate(selectedError.timestamp) }}</el-descriptions-item>
          <el-descriptions-item label="组件">{{ selectedError.componentName || 'N/A' }}</el-descriptions-item>
          <el-descriptions-item label="路由">{{ selectedError.routePath || 'N/A' }}</el-descriptions-item>
        </el-descriptions>
        <pre class="error-stack">{{ selectedError.stack }}</pre>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import type { ErrorRecord } from '@/stores/modules/monitoring'
import { useMonitoringStore } from '@/stores/modules/monitoring'
import dayjs from 'dayjs'
import * as echarts from 'echarts'
import { onMounted, onUnmounted, ref } from 'vue'

const monitoringStore = useMonitoringStore()
const autoRefresh = ref(false)
const refreshInterval = ref<number | null>(null)
const errorDetailVisible = ref(false)
const selectedError = ref<ErrorRecord | null>(null)

// 图表实例
let responseTimeChart: echarts.ECharts | null = null
let requestRateChart: echarts.ECharts | null = null

// 系统状态数据
const systemStats = ref([
  { label: '系统状态', value: '正常', status: 'good' },
  { label: '平均响应时间', value: '200ms', status: 'normal' },
  { label: '错误率', value: '0.1%', status: 'good' },
  { label: 'QPS', value: '100', status: 'normal' }
])

// 错误日志数据
const errorLogs = ref(monitoringStore.recentErrors)

// 格式化日期
const formatDate = (timestamp: number) => {
  return dayjs(timestamp).format('YYYY-MM-DD HH:mm:ss')
}

// 初始化图表
const initCharts = () => {
  // 响应时间图表
  responseTimeChart = echarts.init(document.querySelector('.chart') as HTMLElement)
  responseTimeChart.setOption({
    title: { text: '响应时间趋势' },
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

  // 窗口大小调整时重绘图表
  window.addEventListener('resize', () => {
    responseTimeChart?.resize()
    requestRateChart?.resize()
  })
}

// 更新图表数据
const updateCharts = () => {
  const metrics = monitoringStore.performanceMetrics
  const responseTimeData = metrics
    .filter(m => m.type === 'responseTime')
    .map(m => [m.timestamp, m.value])
  const requestRateData = metrics
    .filter(m => m.type === 'requestRate')
    .map(m => [m.timestamp, m.value])

  responseTimeChart?.setOption({
    series: [{ data: responseTimeData }]
  })
  requestRateChart?.setOption({
    series: [{ data: requestRateData }]
  })
}

// 刷新数据
const refresh = async () => {
  // 更新系统状态
  systemStats.value[0].value = 'Healthy'
  systemStats.value[1].value = `${monitoringStore.averageLoadTime.toFixed(2)}ms`
  systemStats.value[2].value = `${(monitoringStore.errorCount / 100).toFixed(2)}%`

  // 更新错误日志
  errorLogs.value = monitoringStore.recentErrors

  // 更新图表
  updateCharts()
}

// 显示错误详情
const showErrorDetail = (error: ErrorRecord) => {
  selectedError.value = error
  errorDetailVisible.value = true
}

// 切换自动刷新
const toggleAutoRefresh = () => {
  autoRefresh.value = !autoRefresh.value
  if (autoRefresh.value) {
    refreshInterval.value = setInterval(refresh, 5000) as unknown as number
  } else if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
    refreshInterval.value = null
  }
}

// 组件挂载
onMounted(() => {
  initCharts()
  refresh()
})

// 组件卸载
onUnmounted(() => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
  }
  responseTimeChart?.dispose()
  requestRateChart?.dispose()
})
</script>

<style lang="scss">
.monitor-container {
  padding: 20px;

  .metric-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin-bottom: 20px;
  }

  .metric-card {
    padding: 20px;
    border-radius: var(--border-radius-lg);
    background: rgba(255, 255, 255, 0.05);

    .card-header {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 16px;

      .icon-wrapper {
        width: 40px;
        height: 40px;
        border-radius: var(--border-radius-md);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
      }

      &.cpu .icon-wrapper {
        background: rgba(64, 158, 255, 0.1);
        color: var(--primary-color);
      }

      &.memory .icon-wrapper {
        background: rgba(103, 194, 58, 0.1);
        color: var(--success-color);
      }

      &.disk .icon-wrapper {
        background: rgba(230, 162, 60, 0.1);
        color: var(--warning-color);
      }

      &.network .icon-wrapper {
        background: rgba(144, 147, 153, 0.1);
        color: var(--info-color);
      }

      h3 {
        margin: 0;
        font-size: var(--font-size-lg);
      }
    }

    .metric-value {
      font-size: var(--font-size-2xl);
      font-weight: 600;
      margin-bottom: 8px;
    }

    .metric-label {
      color: var(--text-secondary);
      font-size: var(--font-size-sm);
    }
  }

  .charts-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 20px;
    margin-bottom: 20px;
  }

  .chart-card {
    padding: 20px;
    border-radius: var(--border-radius-lg);
    background: rgba(255, 255, 255, 0.05);

    .chart-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;

      h3 {
        margin: 0;
        font-size: var(--font-size-lg);
      }
    }

    .chart-container {
      height: 300px;
    }
  }
}

.chart-tooltip {
  background: rgba(255, 255, 255, 0.9) !important;
  backdrop-filter: blur(8px);
  border-radius: var(--border-radius-md) !important;
  padding: 8px 12px !important;
  color: var(--text-primary) !important;
  border: none !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
}
</style>