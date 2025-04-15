`<template>
  <div class="data-visualization">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stats-card">
          <template #header>
            <div class="card-header">
              <span>总任务数</span>
            </div>
          </template>
          <div class="stats-value">{{ stats.totalTasks }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stats-card">
          <template #header>
            <div class="card-header">
              <span>已完成任务</span>
            </div>
          </template>
          <div class="stats-value">{{ stats.completedTasks }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stats-card">
          <template #header>
            <div class="card-header">
              <span>处理URL数</span>
            </div>
          </template>
          <div class="stats-value">{{ stats.processedUrls }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stats-card">
          <template #header>
            <div class="card-header">
              <span>成功率</span>
            </div>
          </template>
          <div class="stats-value">{{ formatPercent(stats.successRate) }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>任务状态分布</span>
            </div>
          </template>
          <div class="chart-container" ref="pieChartRef"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>最近7天任务趋势</span>
            </div>
          </template>
          <div class="chart-container" ref="lineChartRef"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import axios from 'axios'

const stats = ref({
  totalTasks: 0,
  completedTasks: 0,
  processedUrls: 0,
  successRate: 0
})

const pieChartRef = ref(null)
const lineChartRef = ref(null)
let pieChart = null
let lineChart = null

function formatPercent(value) {
  return \`\${(value * 100).toFixed(1)}%\`
}

async function loadStats() {
  try {
    const response = await axios.get('/api/stats')
    stats.value = response.data
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
}

function initPieChart() {
  pieChart = echarts.init(pieChartRef.value)
  pieChart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [{
      type: 'pie',
      radius: '70%',
      data: [
        { value: 0, name: '已完成' },
        { value: 0, name: '进行中' },
        { value: 0, name: '失败' }
      ],
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }]
  })
}

function initLineChart() {
  lineChart = echarts.init(lineChartRef.value)
  lineChart.setOption({
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: []
    },
    yAxis: {
      type: 'value'
    },
    series: [{
      name: '任务数',
      type: 'line',
      smooth: true,
      data: []
    }]
  })
}

async function updateCharts() {
  try {
    const [taskStatus, taskTrend] = await Promise.all([
      axios.get('/api/stats/task-status'),
      axios.get('/api/stats/task-trend')
    ])

    // 更新饼图数据
    pieChart.setOption({
      series: [{
        data: taskStatus.data
      }]
    })

    // 更新折线图数据
    lineChart.setOption({
      xAxis: {
        data: taskTrend.data.dates
      },
      series: [{
        data: taskTrend.data.counts
      }]
    })
  } catch (error) {
    console.error('Failed to update charts:', error)
  }
}

onMounted(async () => {
  await loadStats()
  initPieChart()
  initLineChart()
  await updateCharts()

  window.addEventListener('resize', () => {
    pieChart?.resize()
    lineChart?.resize()
  })
})

onUnmounted(() => {
  pieChart?.dispose()
  lineChart?.dispose()
})
</script>

<style scoped>
.data-visualization {
  padding: 20px;
}

.stats-card {
  margin-bottom: 20px;
}

.chart-row {
  margin-top: 20px;
}

.chart-card {
  margin-bottom: 20px;
}

.chart-container {
  height: 300px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stats-value {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
  text-align: center;
}
</style>`