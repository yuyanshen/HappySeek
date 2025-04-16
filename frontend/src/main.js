// frontend/src/main.js
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import { createPinia } from 'pinia'
import { createApp } from 'vue'

// 导入样式
import 'element-plus/dist/index.css'
import './styles/index.scss'

// 导入路由和应用
import App from './App.vue'
import router from './router'

// 创建应用实例
const app = createApp(App)

// 注册 Element Plus 图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 配置 Element Plus
app.use(ElementPlus, {
  locale: zhCn,
})

// 初始化 Pinia
const pinia = createPinia()
app.use(pinia)

// 注册路由
app.use(router)

// 全局错误处理
app.config.errorHandler = (err, vm, info) => {
  console.error('Global error:', err)
  console.error('Error info:', info)
}

// 挂载应用
app.mount('#app')