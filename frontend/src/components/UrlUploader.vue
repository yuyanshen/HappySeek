<template>
    <el-upload
      action=""
      :limit="1"
      :show-file-list="false"
      :before-upload="handleBeforeUpload"
      :accept="'.csv,.txt,.json'"
    >
      <el-button type="primary">上传URL文件</el-button>
      <template #tip>
        <div class="el-upload__tip">
          支持CSV/TXT/JSON格式（最多100个URL）
        </div>
      </template>
    </el-upload>
  </template>
  
  <script setup>
  import { ElMessage } from 'element-plus'
  import Papa from 'papaparse'
  
  const emit = defineEmits(['urls-loaded'])
  
  const handleBeforeUpload = (file) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const content = e.target.result
        let urls = []
        
        // 智能识别不同格式
        if (file.name.endsWith('.csv')) {
          const results = Papa.parse(content, { header: false })
          urls = results.data.flat().filter(url => isValidUrl(url))
        } 
        else if (file.name.endsWith('.json')) {
          const data = JSON.parse(content)
          urls = Array.isArray(data) ? data : Object.values(data)
          urls = urls.flat().filter(url => isValidUrl(url))
        }
        else { // TXT
          urls = content.split('\n').filter(url => isValidUrl(url))
        }
        
        if (urls.length > 100) {
          ElMessage.warning(`检测到${urls.length}个URL，仅前100个有效`)
          urls = urls.slice(0, 100)
        }
        
        emit('urls-loaded', urls.join('\n'))
      } catch (error) {
        ElMessage.error('文件解析失败：' + error.message)
      }
    }
    reader.readAsText(file)
    return false // 阻止自动上传
  }
  
  const isValidUrl = (url) => {
    try {
      new URL(url.trim())
      return true
    } catch {
      return false
    }
  }
  </script>