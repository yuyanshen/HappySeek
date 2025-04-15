// frontend/src/main.js
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import 'element-plus/dist/index.css'
import App from './app.vue'
import router from './router'
import errorHandler from './utils/errorHandler'

const app = createApp(App)

// 配置 Element Plus
app.use(ElementPlus, {
  locale: zhCn,
  size: 'default',
  zIndex: 3000
})

// 初始化 Pinia 状态管理
const pinia = createPinia()
app.use(pinia)

// Setup router
app.use(router)

// 添加全局错误处理器
app.config.errorHandler = (err, vm, info) => {
  console.error('Global error:', err)
  errorHandler.handle(err)
}

// 添加全局属性
app.config.globalProperties.$api = {
  baseURL: import.meta.env.VITE_API_URL || '/api'
}

// 挂载应用
app.mount('#app')