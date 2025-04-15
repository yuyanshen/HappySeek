`<template>
  <div class="crawler-config">
    <el-form :model="form" :rules="rules" ref="formRef">
      <el-form-item label="目标URL" prop="urls">
        <el-input
          type="textarea"
          v-model="form.urls"
          :rows="4"
          placeholder="请输入要爬取的URL，每行一个"
        />
      </el-form-item>

      <el-form-item label="爬取深度" prop="depth">
        <el-input-number v-model="form.depth" :min="1" :max="5" />
      </el-form-item>

      <el-form-item label="并发数" prop="concurrency">
        <el-input-number v-model="form.concurrency" :min="1" :max="10" />
      </el-form-item>

      <el-form-item label="请求延迟(ms)" prop="delay">
        <el-slider
          v-model="form.delay"
          :min="0"
          :max="5000"
          :step="100"
          show-input
        />
      </el-form-item>

      <el-form-item>
        <el-button type="primary" @click="submitForm">开始爬取</el-button>
        <el-button @click="resetForm">重置</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useAppStore } from '@/stores/app'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const appStore = useAppStore()
const formRef = ref(null)

const form = reactive({
  urls: '',
  depth: 2,
  concurrency: 3,
  delay: 1000
})

const rules = {
  urls: [
    { required: true, message: '请输入要爬取的URL', trigger: 'blur' },
    { validator: validateUrls, trigger: 'blur' }
  ],
  depth: [
    { required: true, message: '请选择爬取深度', trigger: 'change' }
  ],
  concurrency: [
    { required: true, message: '请选择并发数', trigger: 'change' }
  ]
}

async function validateUrls(rule, value, callback) {
  if (!value) {
    callback(new Error('URL不能为空'))
    return
  }

  const urls = value.split('\n').filter(url => url.trim())
  if (urls.length === 0) {
    callback(new Error('请至少输入一个有效URL'))
    return
  }

  const urlPattern = /^https?:\/\/.+/
  const invalidUrls = urls.filter(url => !urlPattern.test(url.trim()))
  if (invalidUrls.length > 0) {
    callback(new Error('存在无效的URL格式'))
    return
  }

  callback()
}

async function submitForm() {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    
    const urls = form.urls.split('\n').filter(url => url.trim())
    const response = await axios.post('/api/crawl', {
      urls,
      depth: form.depth,
      concurrency: form.concurrency,
      delay: form.delay
    })

    const taskId = response.data.task_id
    appStore.addTask(taskId, {
      urls,
      depth: form.depth,
      progress: 0
    })

    ElMessage.success('爬虫任务已创建')
  } catch (error) {
    if (error.response) {
      ElMessage.error(error.response.data.message || '创建任务失败')
    } else {
      ElMessage.error('表单验证失败，请检查输入')
    }
  }
}

function resetForm() {
  if (formRef.value) {
    formRef.value.resetFields()
  }
}
</script>

<style scoped>
.crawler-config {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}
</style>`