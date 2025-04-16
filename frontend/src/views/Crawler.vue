<!-- frontend/src/views/Crawler.vue -->
<template>
  <div class="crawler-container">
    <div class="header-section">
      <h1>智能网页采集</h1>
      <p class="subtitle">轻松配置和管理您的网页采集任务</p>
    </div>

    <el-row :gutter="40">
      <!-- 配置面板 -->
      <el-col :span="16">
        <div class="config-panel glass-card fade-scale">
          <el-steps :active="activeStep" finish-status="success" class="setup-steps">
            <el-step title="输入URL" />
            <el-step title="配置参数" />
            <el-step title="高级设置" />
          </el-steps>

          <div class="step-content" v-show="activeStep === 0">
            <div class="url-input-section">
              <h3>选择目标网址</h3>
              <p class="step-description">输入您想要采集的网页地址，支持批量输入或文件导入</p>

              <el-form-item>
                <el-input
                  v-model="form.urls"
                  type="textarea"
                  :rows="6"
                  placeholder="每行输入一个URL&#10;例如：https://example.com"
                  :class="{ 'is-focused': isUrlInputFocused }"
                  @focus="isUrlInputFocused = true"
                  @blur="isUrlInputFocused = false"
                />
              </el-form-item>

              <div class="url-tools">
                <UrlUploader @urls-loaded="handleUrlsLoaded" />
                <el-button @click="validateUrls" :icon="Check">验证URL</el-button>
              </div>
            </div>
          </div>

          <div class="step-content" v-show="activeStep === 1">
            <div class="params-section">
              <h3>基础配置</h3>
              <p class="step-description">设置爬取深度和并发数等基本参数</p>

              <el-form :model="form" label-position="top">
                <el-form-item label="爬取深度">
                  <el-slider
                    v-model="form.depth"
                    :min="1"
                    :max="5"
                    :marks="{
                      1: '浅层',
                      3: '中等',
                      5: '深度'
                    }"
                    :step="1"
                  />
                </el-form-item>

                <el-form-item label="并发数">
                  <el-slider
                    v-model="form.concurrency"
                    :min="1"
                    :max="10"
                    :marks="{
                      1: '保守',
                      5: '平衡',
                      10: '激进'
                    }"
                  />
                </el-form-item>

                <el-form-item label="请求间隔 (ms)">
                  <el-slider
                    v-model="form.delay"
                    :min="0"
                    :max="5000"
                    :step="100"
                    :marks="{
                      0: '无延迟',
                      2500: '适中',
                      5000: '保守'
                    }"
                  />
                </el-form-item>
              </el-form>
            </div>
          </div>

          <div class="step-content" v-show="activeStep === 2">
            <div class="advanced-section">
              <h3>高级设置</h3>
              <p class="step-description">配置代理、自定义请求头等高级选项</p>

              <el-form :model="form.advanced" label-position="top">
                <el-form-item label="使用代理">
                  <el-switch v-model="form.advanced.useProxy" />
                </el-form-item>

                <el-form-item label="代理地址" v-if="form.advanced.useProxy">
                  <el-input v-model="form.advanced.proxyUrl" placeholder="http://proxy.example.com:8080" />
                </el-form-item>

                <el-form-item label="自定义User Agent">
                  <el-select v-model="form.advanced.userAgent" class="full-width">
                    <el-option label="Chrome (Windows)" value="chrome-windows" />
                    <el-option label="Chrome (Mac)" value="chrome-mac" />
                    <el-option label="Safari (iOS)" value="safari-ios" />
                    <el-option label="自定义" value="custom" />
                  </el-select>
                </el-form-item>

                <el-form-item label="登录检测">
                  <el-switch v-model="form.advanced.loginDetection" />
                </el-form-item>
              </el-form>
            </div>
          </div>

          <div class="step-actions">
            <el-button
              v-if="activeStep > 0"
              @click="activeStep--"
              :icon="ArrowLeft"
            >
              上一步
            </el-button>
            <el-button
              v-if="activeStep < 2"
              type="primary"
              @click="activeStep++"
              :icon="ArrowRight"
            >
              下一步
            </el-button>
            <el-button
              v-else
              type="primary"
              :loading="loading"
              @click="startCrawling"
              :icon="Launch"
            >
              开始采集
            </el-button>
          </div>
        </div>
      </el-col>

      <!-- 实时状态面板 -->
      <el-col :span="8">
        <div class="status-panel">
          <!-- 任务概览卡片 -->
          <div class="stats-card glass-card fade-scale">
            <h3>任务概览</h3>
            <div class="stats-grid">
              <div class="stat-item">
                <span class="stat-label">队列中</span>
                <span class="stat-value">{{ stats.pending }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">进行中</span>
                <span class="stat-value">{{ stats.running }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">已完成</span>
                <span class="stat-value">{{ stats.completed }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">失败</span>
                <span class="stat-value">{{ stats.failed }}</span>
              </div>
            </div>
          </div>

          <!-- 活动任务列表 -->
          <div class="active-tasks glass-card fade-scale">
            <h3>活动任务</h3>
            <div class="task-list" v-if="activeTasks.length > 0">
              <div v-for="task in activeTasks" :key="task.id" class="task-item">
                <div class="task-info">
                  <span class="task-url">{{ truncateUrl(task.url) }}</span>
                  <el-progress
                    :percentage="task.progress"
                    :status="task.status === 'failed' ? 'exception' : undefined"
                  />
                </div>
              </div>
            </div>
            <div v-else class="no-tasks">
              暂无活动任务
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import UrlUploader from '@/components/UrlUploader.vue'
import { useTaskStore } from '@/stores/task'
import { ArrowLeft, ArrowRight, Check } from '@element-plus/icons-vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { onMounted, reactive, ref } from 'vue'

const taskStore = useTaskStore()
const activeStep = ref(0)
const loading = ref(false)
const isUrlInputFocused = ref(false)

const form = reactive({
  urls: '',
  depth: 3,
  concurrency: 5,
  delay: 1000,
  advanced: {
    useProxy: false,
    proxyUrl: '',
    userAgent: 'chrome-windows',
    loginDetection: true
  }
})

const stats = reactive({
  pending: 0,
  running: 0,
  completed: 0,
  failed: 0
})

const activeTasks = ref([])

const handleUrlsLoaded = (urls) => {
  form.urls = urls
}

const validateUrls = async () => {
  if (!form.urls.trim()) {
    ElMessage.warning('请输入至少一个URL')
    return
  }

  const urls = form.urls.split('\n').filter(url => url.trim())
  loading.value = true

  try {
    const promises = urls.map(url =>
      axios.post('/api/check/url', { url })
        .then(() => ({ url, valid: true }))
        .catch(() => ({ url, valid: false }))
    )

    const results = await Promise.all(promises)
    const invalid = results.filter(r => !r.valid).map(r => r.url)

    if (invalid.length > 0) {
      ElMessage.warning(`以下URL可能无效：\n${invalid.join('\n')}`)
    } else {
      ElMessage.success('所有URL验证通过')
      activeStep.value++
    }
  } catch (error) {
    ElMessage.error('URL验证失败')
  } finally {
    loading.value = false
  }
}

const startCrawling = async () => {
  if (!form.urls.trim()) {
    ElMessage.error('请输入至少一个URL')
    return
  }

  loading.value = true
  try {
    const urls = form.urls.split('\n').filter(url => url.trim())
    const response = await axios.post('/api/crawl', {
      urls,
      depth: form.depth,
      concurrency: form.concurrency,
      delay: form.delay,
      config: form.advanced
    })

    taskStore.addTask({
      id: response.data.task_id,
      url: urls[0] + (urls.length > 1 ? ` 等${urls.length}个` : ''),
      status: 'running',
      progress: 0
    })

    ElMessage.success('任务已启动')
  } catch (error) {
    ElMessage.error('任务提交失败')
  } finally {
    loading.value = false
  }
}

const truncateUrl = (url) => {
  if (url.length > 40) {
    return url.substring(0, 37) + '...'
  }
  return url
}

// 监听任务状态
onMounted(() => {
  activeTasks.value = taskStore.activeTasks

  // 更新统计信息
  const updateStats = () => {
    const tasks = taskStore.activeTasks
    stats.running = tasks.filter(t => t.status === 'running').length
    stats.completed = tasks.filter(t => t.status === 'completed').length
    stats.failed = tasks.filter(t => t.status === 'failed').length
    stats.pending = tasks.filter(t => t.status === 'pending').length
  }

  updateStats()
  // 监听任务状态变化
  taskStore.$subscribe((mutation, state) => {
    updateStats()
    activeTasks.value = state.activeTasks
  })
})
</script>

<style scoped>
.crawler-container {
  max-width: 1440px;
  margin: 0 auto;
  padding: 40px;
}

.header-section {
  text-align: center;
  margin-bottom: 40px;
}

.header-section h1 {
  font-size: var(--font-size-4xl);
  background: linear-gradient(135deg, var(--primary-color), #5ac8fa);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 8px;
}

.subtitle {
  color: var(--text-secondary);
  font-size: var(--font-size-lg);
}

.config-panel {
  padding: 40px;
  margin-bottom: 20px;
}

.setup-steps {
  margin-bottom: 40px;
}

.step-content {
  margin-bottom: 40px;
}

.step-description {
  color: var(--text-secondary);
  margin-bottom: 24px;
}

.url-input-section,
.params-section,
.advanced-section {
  animation: fadeScale 0.3s ease;
}

.url-tools {
  display: flex;
  gap: 16px;
  margin-top: 16px;
}

.step-actions {
  display: flex;
  justify-content: space-between;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

/* Status Panel Styles */
.status-panel {
  position: sticky;
  top: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.stats-card,
.active-tasks {
  padding: 24px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-top: 20px;
}

.stat-item {
  text-align: center;
  padding: 16px;
  border-radius: var(--border-radius-md);
  background: rgba(255, 255, 255, 0.05);
}

.stat-label {
  display: block;
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  margin-bottom: 8px;
}

.stat-value {
  font-size: var(--font-size-2xl);
  font-weight: 600;
  color: var(--primary-color);
}

.task-list {
  margin-top: 16px;
}

.task-item {
  padding: 16px;
  border-radius: var(--border-radius-md);
  background: rgba(255, 255, 255, 0.05);
  margin-bottom: 12px;
}

.task-url {
  display: block;
  margin-bottom: 8px;
  color: var(--text-secondary);
}

.no-tasks {
  text-align: center;
  color: var(--text-secondary);
  padding: 40px 0;
}

/* Responsive Design */
@media (max-width: 1200px) {
  .crawler-container {
    padding: 20px;
  }

  .el-row {
    flex-direction: column;
  }

  .el-col {
    width: 100% !important;
    max-width: 100% !important;
    flex: 0 0 100% !important;
  }

  .status-panel {
    position: static;
    margin-top: 20px;
  }
}
</style>