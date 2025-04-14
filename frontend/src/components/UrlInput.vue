<template>
    <div>
      <el-form-item label="目标网址" prop="urls">
        <el-input
          v-model="form.urls"
          type="textarea"
          :rows="5"
          placeholder="每行一个URL"
          @blur="validateUrls"
        ></el-input>
        <div class="url-status-list">
          <div v-for="(url, index) in urlList" :key="index" class="url-item">
            <span>{{ url }}</span>
            <el-icon v-if="urlStatus[url] === 'success'" color="#67C23A">
              <CircleCheck />
            </el-icon>
            <el-icon v-else-if="urlStatus[url] === 'error'" color="#F56C6C">
              <CircleClose />
            </el-icon>
            <el-icon v-else color="#E6A23C">
              <Loading />
            </el-icon>
          </div>
        </div>
      </el-form-item>
    </div>
  </template>
  
  <script setup>
  import { ref, computed } from 'vue'
  import { CircleCheck, CircleClose, Loading } from '@element-plus/icons-vue'
  import axios from 'axios'
  
  const props = defineProps(['modelValue'])
  const emit = defineEmits(['update:modelValue'])
  
  const form = ref({
    urls: props.modelValue
  })
  
  const urlList = computed(() => {
    return form.value.urls.split('\n').filter(url => url.trim())
  })
  
  const urlStatus = ref({})
  
  const validateUrls = async () => {
    emit('update:modelValue', form.value.urls)
    
    for (const url of urlList.value) {
      try {
        urlStatus.value[url] = 'loading'
        await axios.head(url, { timeout: 3000 })
        urlStatus.value[url] = 'success'
      } catch (error) {
        urlStatus.value[url] = 'error'
      }
    }
  }
  </script>
  
  <style scoped>
  .url-status-list {
    margin-top: 10px;
  }
  .url-item {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 4px 0;
  }
  </style>