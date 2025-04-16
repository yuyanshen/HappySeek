<template>
  <div class="task-monitor glass-card">
    <div class="monitor-header">
      <div class="header-content">
        <h2>任务监控中心</h2>
        <div class="status-badges">
          <el-badge :value="runningTasks.length" type="primary" class="status-badge">
            运行中
          </el-badge>
          <el-badge :value="pendingTasks.length" type="warning" class="status-badge">
            等待中
          </el-badge>
        </div>
      </div>
      <div class="header-actions">
        <el-button-group>
          <el-tooltip content="刷新" placement="top">
            <el-button :icon="RefreshRight" circle @click="refreshTasks" />
          </el-tooltip>
          <el-tooltip content="清除已完成" placement="top">
            <el-button :icon="Delete" circle @click="clearCompletedTasks" />
          </el-tooltip>
        </el-button-group>
      </div>
    </div>

    <div class="tasks-container">
      <!-- 运行中的任务 -->
      <div class="task-section" v-if="runningTasks.length">
        <h3 class="section-title">运行中的任务</h3>
        <div class="task-grid">
          <div v-for="task in runningTasks" :key="task.id" class="task-card fade-scale">
            <div class="task-header">
              <span class="task-type" :class="task.type">{{ task.type }}</span>
              <el-dropdown trigger="click">
                <el-icon class="more-actions"><MoreFilled /></el-icon>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item @click="pauseTask(task.id)">
                      暂停
                    </el-dropdown-item>
                    <el-dropdown-item @click="cancelTask(task.id)" divided>
                      取消
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>

            <div class="task-content">
              <div class="task-info">
                <h4 class="task-url">{{ truncateUrl(task.url) }}</h4>
                <p class="task-meta">
                  深度：{{ task.depth }} | 并发：{{ task.concurrency }}
                </p>
              </div>

              <div class="progress-section">
                <div class="progress-header">
                  <span class="progress-text">{{ task.progress }}%</span>
                  <span class="time-elapsed">{{ formatDuration(task.elapsed) }}</span>
                </div>
                <el-progress
                  :percentage="task.progress"
                  :status="getProgressStatus(task)"
                  :stroke-width="8"
                  :show-text="false"
                />
              </div>

              <div class="task-stats">
                <div class="stat-item">
                  <span class="stat-label">已采集</span>
                  <span class="stat-value">{{ task.collected }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">待处理</span>
                  <span class="stat-value">{{ task.pending }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">错误</span>
                  <span class="stat-value error">{{ task.errors }}</span>
                </div>
              </div>
            </div>

            <div class="task-logs" v-if="task.recentLogs?.length">
              <div class="log-header">
                <span>最近日志</span>
                <el-button type="text" size="small" @click="viewFullLogs(task.id)">
                  查看全部
                </el-button>
              </div>
              <div class="log-content">
                <div v-for="log in task.recentLogs" :key="log.time" class="log-item">
                  <span class="log-time">{{ formatTime(log.time) }}</span>
                  <span class="log-message" :class="log.type">{{ log.message }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 等待中的任务 -->
      <div class="task-section" v-if="pendingTasks.length">
        <h3 class="section-title">等待队列</h3>
        <el-table :data="pendingTasks" style="width: 100%">
          <el-table-column prop="url" label="URL" min-width="200">
            <template #default="{ row }">
              <el-tooltip :content="row.url" placement="top">
                <span>{{ truncateUrl(row.url) }}</span>
              </el-tooltip>
            </template>
          </el-table-column>
          <el-table-column prop="type" label="类型" width="100" />
          <el-table-column prop="depth" label="深度" width="80" align="center" />
          <el-table-column label="操作" width="120" align="center">
            <template #default="{ row }">
              <el-button size="small" @click="prioritizeTask(row.id)">
                优先执行
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 任务日志对话框 -->
    <el-dialog
      v-model="logsDialogVisible"
      title="任务日志"
      width="80%"
      class="logs-dialog"
    >
      <div class="logs-container">
        <div v-for="log in selectedTaskLogs" :key="log.time" class="log-item">
          <span class="log-time">{{ formatTime(log.time) }}</span>
          <span class="log-message" :class="log.type">{{ log.message }}</span>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { useTaskStore } from '@/stores/task'
import { Delete, MoreFilled, RefreshRight } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { computed, ref } from 'vue'

const taskStore = useTaskStore()
const logsDialogVisible = ref(false)
const selectedTaskLogs = ref([])

// 计算属性
const runningTasks = computed(() =>
  taskStore.activeTasks.filter(t => t.status === 'running')
)

const pendingTasks = computed(() =>
  taskStore.pendingTasks
)

// 方法
const truncateUrl = (url) => {
  if (url.length > 40) return url.slice(0, 37) + '...'
  return url
}

const formatDuration = (ms) => {
  if (!ms) return '0s'
  const seconds = Math.floor(ms / 1000)
  if (seconds < 60) return `${seconds}s`
  const minutes = Math.floor(seconds / 60)
  return `${minutes}m ${seconds % 60}s`
}

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString()
}

const getProgressStatus = (task) => {
  if (task.status === 'failed') return 'exception'
  if (task.status === 'completed') return 'success'
  return ''
}

const refreshTasks = () => {
  taskStore.refreshTasks()
  ElMessage.success('已刷新任务状态')
}

const clearCompletedTasks = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清除所有已完成的任务吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    taskStore.clearCompletedTasks()
    ElMessage.success('已清除完成任务')
  } catch {
    // 用户取消操作
  }
}

const pauseTask = async (taskId) => {
  try {
    await taskStore.pauseTask(taskId)
    ElMessage.success('任务已暂停')
  } catch (error) {
    ElMessage.error('暂停任务失败')
  }
}

const cancelTask = async (taskId) => {
  try {
    await ElMessageBox.confirm(
      '确定要取消该任务吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await taskStore.cancelTask(taskId)
    ElMessage.success('任务已取消')
  } catch {
    // 用户取消操作
  }
}

const prioritizeTask = (taskId) => {
  taskStore.prioritizeTask(taskId)
  ElMessage.success('任务已设为优先')
}

const viewFullLogs = (taskId) => {
  const task = taskStore.activeTasks.find(t => t.id === taskId)
  if (task) {
    selectedTaskLogs.value = task.logs || []
    logsDialogVisible.value = true
  }
}
</script>

<style scoped>
.task-monitor {
  padding: 24px;
}

.monitor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 24px;
}

.header-content h2 {
  margin: 0;
  font-size: var(--font-size-2xl);
  background: linear-gradient(135deg, var(--primary-color), #5ac8fa);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.status-badges {
  display: flex;
  gap: 12px;
}

.status-badge {
  margin-top: 4px;
}

.tasks-container {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.task-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.section-title {
  font-size: var(--font-size-lg);
  color: var(--text-secondary);
  margin: 0;
}

.task-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.task-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: var(--border-radius-lg);
  overflow: hidden;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: rgba(255, 255, 255, 0.02);
}

.task-type {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: var(--font-size-sm);
}

.task-type.crawler { background: rgba(0, 102, 204, 0.1); color: var(--primary-color); }
.task-type.parser { background: rgba(52, 199, 89, 0.1); color: var(--success-color); }

.more-actions {
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: background-color var(--transition-fast);
}

.more-actions:hover {
  background: rgba(255, 255, 255, 0.1);
}

.task-content {
  padding: 16px;
}

.task-info {
  margin-bottom: 16px;
}

.task-url {
  margin: 0 0 8px;
  font-size: var(--font-size-base);
}

.task-meta {
  margin: 0;
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.progress-section {
  margin-bottom: 16px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.progress-text {
  font-weight: 500;
}

.time-elapsed {
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
}

.task-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-top: 16px;
}

.stat-item {
  text-align: center;
}

.stat-label {
  display: block;
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  margin-bottom: 4px;
}

.stat-value {
  font-weight: 500;
}

.stat-value.error {
  color: var(--error-color);
}

.task-logs {
  padding: 16px;
  background: rgba(0, 0, 0, 0.2);
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.log-content {
  font-family: monospace;
  font-size: var(--font-size-sm);
}

.log-item {
  display: flex;
  gap: 8px;
  margin-bottom: 4px;
}

.log-time {
  color: var(--text-secondary);
  white-space: nowrap;
}

.log-message {
  word-break: break-all;
}

.log-message.error { color: var(--error-color); }
.log-message.warning { color: var(--warning-color); }
.log-message.success { color: var(--success-color); }

/* 日志对话框样式 */
.logs-dialog :deep(.el-dialog__body) {
  padding: 0;
}

.logs-container {
  height: 60vh;
  overflow-y: auto;
  padding: 20px;
  background: var(--surface-color);
  font-family: monospace;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .task-grid {
    grid-template-columns: 1fr;
  }

  .monitor-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .header-actions {
    width: 100%;
    display: flex;
    justify-content: flex-end;
  }
}
</style>