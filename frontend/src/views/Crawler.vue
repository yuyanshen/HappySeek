<!-- frontend/src/views/Crawler.vue -->
<template>
    <div class="crawler-container">
      <el-card shadow="hover" class="main-card">
        <template #header>
          <div class="card-header">
            <h2>🌐 智能网页元素采集系统</h2>
          </div>
        </template>
  
        <el-form :model="form" label-width="120px">
          <el-form-item label="目标网址">
            <el-input
              v-model="form.urls"
              type="textarea"
              :rows="5"
              placeholder="每行一个URL，例如：
  https://example.com
  https://example.org"
            ></el-input>
          </el-form-item>
  
          <el-form-item label="或上传文件">
            <el-upload
              action=""
              :auto-upload="false"
              :on-change="handleFileUpload"
            >
              <el-button type="primary">选择TXT文件</el-button>
              <template #tip>
                <div class="el-upload__tip">仅支持包含URL列表的txt文件</div>
              </template>
            </el-upload>
          </el-form-item>
  
          <el-form-item label="爬取深度">
            <el-slider
              v-model="form.depth"
              :min="1"
              :max="5"
              show-input
            ></el-slider>
          </el-form-item>
        </el-form>
  
        <div class="action-buttons">
          <el-button 
            type="success" 
            :loading="loading"
            @click="startCrawling"
          >
            🚀 开始采集
          </el-button>
          <el-button @click="resetForm">重置</el-button>
        </div>
  
        <!-- 任务进度展示 -->
        <el-divider />
        <el-table :data="tasks" style="width: 100%">
          <el-table-column prop="id" label="任务ID" width="120" />
          <el-table-column prop="status" label="状态" width="120">
            <template #default="{ row }">
              <el-tag :type="statusTagType(row.status)">
                {{ row.status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="progress" label="进度" width="180">
            <template #default="{ row }">
              <el-progress 
                :percentage="row.progress" 
                :status="row.status === 'failed' ? 'exception' : undefined"
              />
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </template>
  
  <script setup>
  import { ref, reactive } from 'vue'
  import axios from 'axios'
  
  const form = reactive({
    urls: '',
    depth: 3
  })
  
  const loading = ref(false)
  const tasks = ref([])
  
  const statusTagType = (status) => {
    const map = {
      'running': 'warning',
      'completed': 'success',
      'failed': 'danger'
    }
    return map[status] || ''
  }
  
  const handleFileUpload = (file) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      form.urls = e.target.result
    }
    reader.readAsText(file.raw)
  }
  
  const startCrawling = async () => {
    if (!form.urls.trim()) {
      ElMessage.error('请输入至少一个URL')
      return
    }
  
    loading.value = true
    try {
      const response = await axios.post('/api/crawl', {
        urls: form.urls.split('\n').filter(url => url.trim()),
        depth: form.depth
      })
      tasks.value.push({
        id: response.data.task_id,
        status: 'running',
        progress: 0
      })
      ElMessage.success('任务已启动')
      pollTaskStatus(response.data.task_id)
    } catch (error) {
      ElMessage.error('任务提交失败')
    } finally {
      loading.value = false
    }
  }
  
  const pollTaskStatus = (taskId) => {
    const interval = setInterval(async () => {
      try {
        const { data } = await axios.get(`/api/tasks/${taskId}`)
        const task = tasks.value.find(t => t.id === taskId)
        if (task) {
          task.status = data.status
          task.progress = data.progress
          
          if (['completed', 'failed'].includes(data.status)) {
            clearInterval(interval)
            if (data.status === 'completed') {
              ElNotification({
                title: '任务完成',
                message: `已采集 ${data.result_count} 个元素`,
                type: 'success'
              })
            }
          }
        }
      } catch (error) {
        clearInterval(interval)
      }
    }, 2000)
  }
  
  const resetForm = () => {
    form.urls = ''
    form.depth = 3
  }
  </script>
  
  <style scoped>
  .crawler-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
  }
  .main-card {
    border-radius: 12px;
  }
  .card-header {
    text-align: center;
  }
  .action-buttons {
    display: flex;
    justify-content: center;
    gap: 20px;
    margin-top: 30px;
  }
  </style>