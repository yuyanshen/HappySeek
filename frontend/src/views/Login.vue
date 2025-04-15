<!-- Login.vue -->
<template>
  <div class="login-page">
    <div class="login-container fade-scale">
      <div class="login-content glass-card">
        <!-- Logo -->
        <div class="brand-section">
          <div class="logo">
            <svg class="logo-icon" viewBox="0 0 24 24">
              <path d="M12 2L2 7v10l10 5 10-5V7L12 2zm0 2.8L19.5 8 12 11.2 4.5 8 12 4.8zM4 16.2V9.8l7 3.2v6.4l-7-3.2zm9 3.2v-6.4l7-3.2v6.4l-7 3.2z" fill="currentColor"/>
            </svg>
            <h1 class="brand-name">HappySeek</h1>
          </div>
          <p class="tagline">智能网页元素采集系统</p>
        </div>

        <!-- Login Form -->
        <div class="form-section">
          <el-form 
            :model="loginForm" 
            :rules="rules" 
            ref="loginFormRef"
            class="login-form"
          >
            <el-form-item prop="username">
              <el-input
                v-model="loginForm.username"
                placeholder="用户名"
                :prefix-icon="User"
              />
            </el-form-item>
            
            <el-form-item prop="password">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="密码"
                :prefix-icon="Lock"
                show-password
              />
            </el-form-item>

            <div class="form-options">
              <el-checkbox v-model="rememberMe">记住我</el-checkbox>
              <a href="#" class="forgot-link">忘记密码？</a>
            </div>
            
            <el-button 
              type="primary" 
              class="submit-btn" 
              :loading="loading"
              @click="handleLogin"
            >
              登录
            </el-button>

            <div class="register-section">
              <span>还没有账号？</span>
              <router-link to="/register" class="register-link">立即注册</router-link>
            </div>
          </el-form>
        </div>
      </div>

      <!-- Floating Elements -->
      <div class="floating-elements">
        <div class="floating-circle circle-1"></div>
        <div class="floating-circle circle-2"></div>
        <div class="floating-circle circle-3"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()

const loginFormRef = ref(null)
const loading = ref(false)
const rememberMe = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  try {
    await loginFormRef.value.validate()
    loading.value = true
    
    await appStore.login(loginForm)
    
    ElMessage({
      type: 'success',
      message: '登录成功',
      duration: 2000
    })
    
    const redirect = route.query.redirect || '/'
    router.push(redirect)
  } catch (error) {
    ElMessage({
      type: 'error',
      message: error.message || '登录失败',
      duration: 3000
    })
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #f5f5f7 0%, #ffffff 100%);
  position: relative;
  overflow: hidden;
}

.login-container {
  width: 100%;
  max-width: 960px;
  margin: 0 40px;
  position: relative;
  z-index: 1;
}

.login-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
  padding: 60px;
  border-radius: var(--border-radius-xl);
  position: relative;
}

.brand-section {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;
}

.logo {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.logo-icon {
  width: 48px;
  height: 48px;
  color: var(--primary-color);
}

.brand-name {
  font-size: var(--font-size-3xl);
  font-weight: 700;
  background: linear-gradient(135deg, var(--primary-color), #5ac8fa);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.tagline {
  font-size: var(--font-size-xl);
  color: var(--text-secondary);
  margin: 0;
}

.form-section {
  padding: 20px 0;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: -8px;
}

.forgot-link {
  color: var(--primary-color);
  text-decoration: none;
  font-size: var(--font-size-sm);
  transition: var(--transition-fast);
}

.forgot-link:hover {
  color: var(--text-primary);
}

.submit-btn {
  width: 100%;
  height: 48px;
  font-size: var(--font-size-lg);
  margin-top: 16px;
}

.register-section {
  text-align: center;
  margin-top: 24px;
  color: var(--text-secondary);
}

.register-link {
  color: var(--primary-color);
  text-decoration: none;
  margin-left: 8px;
  transition: var(--transition-fast);
}

.register-link:hover {
  color: var(--text-primary);
}

/* Floating Elements Animation */
.floating-elements {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.floating-circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.1;
  background: linear-gradient(135deg, var(--primary-color), #5ac8fa);
}

.circle-1 {
  width: 300px;
  height: 300px;
  top: -150px;
  left: -150px;
  animation: float 20s infinite;
}

.circle-2 {
  width: 200px;
  height: 200px;
  top: 50%;
  right: -100px;
  animation: float 15s infinite reverse;
}

.circle-3 {
  width: 150px;
  height: 150px;
  bottom: -75px;
  left: 50%;
  animation: float 18s infinite;
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0);
  }
  25% {
    transform: translate(50px, -50px);
  }
  50% {
    transform: translate(0, -100px);
  }
  75% {
    transform: translate(-50px, -50px);
  }
}

/* Responsive Design */
@media (max-width: 768px) {
  .login-container {
    margin: 20px;
  }

  .login-content {
    grid-template-columns: 1fr;
    padding: 40px 20px;
  }

  .brand-section {
    text-align: center;
    align-items: center;
  }

  .form-section {
    padding: 0;
  }
}
</style>