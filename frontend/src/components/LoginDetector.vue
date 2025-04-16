<template>
    <el-dialog v-model="visible" title="检测到登录页面">
      <el-form :model="loginForm" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="loginForm.username" autocomplete="off" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="loginForm.password" type="password" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确认</el-button>
      </template>
    </el-dialog>
  </template>

  <script setup>
  import { defineExpose, ref } from 'vue'

  const visible = ref(false)
  const loginForm = ref({
    username: '',
    password: '',
    url: ''
  })

  const showDialog = (url) => {
    loginForm.value.url = url
    visible.value = true
  }

  const handleSubmit = () => {
    // 这里调用API保存登录凭证
    console.log('提交登录信息:', loginForm.value)
    visible.value = false
  }

  defineExpose({ showDialog })
  </script>