// frontend/src/main.js
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
import errorHandler from './utils/errorHandler'

// Create app instance
const app = createApp(App)

// Initialize Pinia store
const pinia = createPinia()
app.use(pinia)

// Setup router
app.use(router)

// Setup Element Plus
app.use(ElementPlus)

// Initialize error handler
errorHandler.init()

// Mount the app
app.mount('#app')