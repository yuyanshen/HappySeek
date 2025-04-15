<template>
  <div class="dashboard-container">
    <!-- 顶部统计卡片 -->
    <el-row :gutter="20" class="stat-cards">
      <el-col :span="6" v-for="stat in statistics" :key="stat.title">
        <div class="stat-card glass-card fade-scale">
          <div class="stat-icon" :class="stat.type">
            <el-icon><component :is="stat.icon" /></el-icon>
          </div>
          <div class="stat-content">
            <h3 class="stat-value">{{ stat.value }}</h3>
            <p class="stat-title">{{ stat.title }}</p>
          </div>
          <div class="stat-trend" :class="stat.trend > 0 ? 'positive' : 'negative'">
            {{ Math.abs(stat.trend) }}% {{ stat.trend > 0 ? '↑' : '↓' }}
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 主要图表区域 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="16">
        <div class="chart-card glass-card fade-scale">
          <div class="chart-header">
            <h3>爬取任务趋势</h3>
            <el-radio-group v-model="timeRange" size="small">
              <el-radio-button label="day">今日</el-radio-button>
              <el-radio-button label="week">本周</el-radio-button>
              <el-radio-button label="month">本月</el-radio-button>
            </el-radio-group>
          </div>
          <div class="chart-container" ref="trendChartRef"></div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="chart-card glass-card fade-scale">
          <div class="chart-header">
            <h3>资源分布</h3>
            <el-select v-model="resourceType" size="small">
              <el-option label="URL类型" value="url" />
              <el-option label="内容类型" value="content" />
            </el-select>
          </div>
          <div class="chart-container" ref="distributionChartRef"></div>
        </div>
      </el-col>
    </el-row>

    <!-- 实时监控面板 -->
    <div class="monitor-panel glass-card fade-scale">
      <div class="panel-header">
        <h3>实时任务监控</h3>
        <el-button-group>
          <el-button size="small" :type="viewMode === 'list' ? 'primary' : ''" @click="viewMode = 'list'">
            <el-icon><List /></el-icon>
          </el-button>
          <el-button size="small" :type="viewMode === 'grid' ? 'primary' : ''" @click="viewMode = 'grid'">
            <el-icon><Grid /></el-icon>
          </el-button>
        </el-button-group>
      </div>

      <div class="task-container" :class="viewMode">
        <template v-if="activeTasks.length">
          <div v-for="task in activeTasks" :key="task.id" class="task-card">
            <div class="task-header">
              <span class="task-title">{{ truncateUrl(task.url) }}</span>
              <el-tag :type="getStatusType(task.status)" size="small">
                {{ getStatusText(task.status) }}
              </el-tag>
            </div>
            <el-progress 
              :percentage="task.progress" 
              :status="task.status === 'failed' ? 'exception' : undefined"
            />
            <div class="task-details">
              <div class="detail-item">
                <span class="label">深度</span>
                <span class="value">{{ task.depth }}</span>
              </div>
              <div class="detail-item">
                <span class="label">已采集</span>
                <span class="value">{{ task.collected || 0 }}</span>
              </div>
              <div class="detail-item">
                <span class="label">耗时</span>
                <span class="value">{{ formatDuration(task.duration) }}</span>
              </div>
            </div>
          </div>
        </template>
        <div v-else class="no-tasks">
          暂无活动任务
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useTaskStore } from '@/stores/task'
import { List, Grid } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const taskStore = useTaskStore()
const timeRange = ref('day')
const resourceType = ref('url')
const viewMode = ref('grid')
const trendChartRef = ref(null)
const distributionChartRef = ref(null)
let trendChart = null
let distributionChart = null

// 统计数据
const statistics = reactive([
  {
    title: '今日任务数',
    value: 0,
    icon: 'Document',
    type: 'primary',
    trend: 12.5
  },
  {
    title: '成功率',
    value: '98.2%',
    icon: 'Success',
    type: 'success',
    trend: 2.1
  },
  {
    title: '平均耗时',
    value: '2.5min',
    icon: 'Timer',
    type: 'warning',
    trend: -5.3
  },
  {
    title: '已采集数据',
    value: '12.5K',
    icon: 'Collection',
    type: 'info',
    trend: 8.7
  }
])

// 初始化趋势图表
const initTrendChart = () => {
  trendChart = echarts.init(trendChartRef.value)
  trendChart.setOption({
    grid: {
      top: 40,
      right: 20,
      bottom: 40,
      left: 60
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.9)',
      borderWidth: 0,
      textStyle: {
        color: '#333'
      }
    },
    xAxis: {
      type: 'category',
      data: ['00:00', '03:00', '06:00', '09:00', '12:00', '15:00', '18:00', '21:00'],
      axisLine: {
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.1)'
        }
      },
      axisLabel: {
        color: 'rgba(255, 255, 255, 0.6)'
      }
    },
    yAxis: {
      type: 'value',
      splitLine: {
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.1)'
        }
      },
      axisLabel: {
        color: 'rgba(255, 255, 255, 0.6)'
      }
    },
    series: [
      {
        name: '任务数',
        type: 'line',
        smooth: true,
        data: [30, 40, 20, 50, 80, 60, 90, 70],
        lineStyle: {
          width: 3,
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#0066cc' },
            { offset: 1, color: '#5ac8fa' }
          ])
        },
        areaStyle: {
          opacity: 0.1,
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#0066cc' },
            { offset: 1, color: 'transparent' }
          ])
        },
        symbol: 'circle',
        symbolSize: 8
      }
    ]
  })
}

// 初始化分布图表
const initDistributionChart = () => {
  distributionChart = echarts.init(distributionChartRef.value)
  distributionChart.setOption({
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(255, 255, 255, 0.9)',
      borderWidth: 0,
      textStyle: {
        color: '#333'
      }
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center',
      textStyle: {
        color: 'rgba(255, 255, 255, 0.6)'
      }
    },
    series: [
      {
        name: 'URL类型',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderColor: 'rgba(255, 255, 255, 0.1)',
          borderWidth: 2
        },
        label: {
          show: false
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '14',
            fontWeight: 'bold'
          }
        },
        data: [
          { value: 335, name: '新闻页' },
          { value: 310, name: '列表页' },
          { value: 234, name: '详情页' },
          { value: 135, name: '其他' }
        ]
      }
    ]
  })
}

// 工具函数
const truncateUrl = (url) => {
  if (!url) return ''
  if (url.length > 40) {
    return url.substring(0, 37) + '...'
  }
  return url
}

const formatDuration = (ms) => {
  if (!ms) return '0s'
  const seconds = Math.floor(ms / 1000)
  if (seconds < 60) return `${seconds}s`
  const minutes = Math.floor(seconds / 60)
  return `${minutes}m ${seconds % 60}s`
}

const getStatusType = (status) => {
  const types = {
    running: 'primary',
    completed: 'success',
    failed: 'danger',
    pending: 'info'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    running: '进行中',
    completed: '已完成',
    failed: '失败',
    pending: '等待中'
  }
  return texts[status] || status
}

// 生命周期钩子
onMounted(() => {
  initTrendChart()
  initDistributionChart()

  window.addEventListener('resize', () => {
    trendChart?.resize()
    distributionChart?.resize()
  })
})

onUnmounted(() => {
  trendChart?.dispose()
  distributionChart?.dispose()
})
</script>

<style scoped>
.dashboard-container {
  padding: 40px;
  max-width: 1440px;
  margin: 0 auto;
}

.stat-cards {
  margin-bottom: 24px;
}

.stat-card {
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--border-radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-icon.primary { background: rgba(0, 102, 204, 0.1); color: var(--primary-color); }
.stat-icon.success { background: rgba(52, 199, 89, 0.1); color: var(--success-color); }
.stat-icon.warning { background: rgba(255, 149, 0, 0.1); color: var(--warning-color); }
.stat-icon.info { background: rgba(134, 134, 139, 0.1); color: var(--text-secondary); }

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: var(--font-size-2xl);
  margin: 0;
  font-weight: 600;
}

.stat-title {
  color: var(--text-secondary);
  margin: 4px 0 0;
  font-size: var(--font-size-sm);
}

.stat-trend {
  font-size: var(--font-size-sm);
  font-weight: 500;
}

.stat-trend.positive { color: var(--success-color); }
.stat-trend.negative { color: var(--error-color); }

.chart-row {
  margin-bottom: 24px;
}

.chart-card {
  padding: 24px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.chart-container {
  height: 360px;
}

.monitor-panel {
  padding: 24px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.task-container {
  display: grid;
  gap: 20px;
}

.task-container.grid {
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
}

.task-container.list {
  grid-template-columns: 1fr;
}

.task-card {
  padding: 20px;
  border-radius: var(--border-radius-md);
  background: rgba(255, 255, 255, 0.05);
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.task-title {
  font-weight: 500;
}

.task-details {
  margin-top: 16px;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.detail-item {
  text-align: center;
}

.detail-item .label {
  display: block;
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  margin-bottom: 4px;
}

.detail-item .value {
  font-weight: 500;
}

.no-tasks {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary);
}

/* Responsive Design */
@media (max-width: 1200px) {
  .dashboard-container {
    padding: 20px;
  }

  .stat-cards .el-col {
    margin-bottom: 20px;
  }

  .chart-row .el-col {
    width: 100% !important;
  }

  .task-container.grid {
    grid-template-columns: 1fr;
  }
}
</style>