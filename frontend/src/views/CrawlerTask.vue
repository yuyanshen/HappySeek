<script setup>
import { checkLoginPage } from '@/api/crawler'
import LoginDetector from '@/components/LoginDetector.vue'
import { ref } from 'vue'

const loginDetector = ref()
const taskUrls = ref([])

// 在任务启动前检测
const startTask = async () => {
  for (const url of taskUrls.value) {
    const res = await checkLoginPage(url)
    if (res.requiresLogin) {
      loginDetector.value.showDialog(url)
      await new Promise(resolve => {
        // 等待用户输入凭证
        const unwatch = watch(loginDetector, (val) => {
          if (!val.visible) {
            unwatch()
            resolve()
          }
        })
      })
    }
  }
  // 继续执行爬取...
}
</script>

<template>
  <LoginDetector ref="loginDetector" />
  <!-- 其他任务界面代码 -->
</template>