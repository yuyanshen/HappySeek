<template>
    <div class="task-monitor">
      <el-card>
        <template #header>
          <div class="monitor-header">
            <span>实时爬取进度</span>
            <el-tag>并发数: {{ activeTasks.length }}/10</el-tag>
          </div>
        </template>
  
        <el-table :data="activeTasks" style="width: 100%">
          <el-table-column prop="url" label="目标网站" width="200">
            <template #default="{ row }">
              <el-link :href="row.url" target="_blank">{{ row.url }}</el-link>
            </template>
          </el-table-column>
          <el-table-column label="进度" width="300">
            <template #default="{ row }">
              <el-progress 
                :percentage="row.progress" 
                :status="row.status === 'failed' ? 'exception' : undefined"
                :text-inside="true"
              >
                <span>{{ row.statusText }}</span>
              </el-progress>
            </template>
          </el-table-column>
          <el-table-column label="详情">
            <template #default="{ row }">
              <el-collapse>
                <el-collapse-item title="详细日志">
                  <div v-for="(log, idx) in row.logs" :key="idx" class="log-line">
                    [{{ log.time }}] {{ log.message }}
                  </div>
                </el-collapse-item>
              </el-collapse>
            </template>
          </el-table-column>
        </el-table>
  
        <div v-if="pendingTasks.length > 0" class="pending-section">
          <h4>等待队列 ({{ pendingTasks.length }})</h4>
          <el-tag 
            v-for="(task, idx) in pendingTasks" 
            :key="'pending-'+idx"
            type="info"
          >
            {{ task.url }}
          </el-tag>
        </div>
      </el-card>
    </div>
  </template>
  
  <script setup>
  import { computed } from 'vue'
  import { useStore } from 'vuex'
  
  const store = useStore()
  
  const activeTasks = computed(() => 
    store.state.task.activeTasks.map(t => ({
      ...t,
      statusText: getStatusText(t.status, t.progress)
    }))
  )
  
  const pendingTasks = computed(() => store.state.task.pendingTasks)
  
  const getStatusText = (status, progress) => {
    const map = {
      running: `爬取中 ${progress}%`,
      analyzing: '分析页面结构中...',
      waiting: '等待执行',
      failed: '爬取失败',
      completed: '已完成'
    }
    return map[status] || status
  }
  </script>
  
  <style scoped>
  .monitor-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .log-line {
    font-family: monospace;
    font-size: 12px;
    margin: 2px 0;
  }
  .pending-section {
    margin-top: 20px;
  }
  .pending-section .el-tag {
    margin-right: 8px;
    margin-bottom: 8px;
  }
  </style>