// frontend/src/stores/app.js
import { defineStore } from 'pinia'
import axios from 'axios'

export const useAppStore = defineStore('app', {
  state: () => ({
    loading: false,
    config: null,
    wsConnected: false,
    offlineMode: false,
    user: null,
    token: localStorage.getItem('token'),
    settings: {
      theme: localStorage.getItem('theme') || 'light',
      language: localStorage.getItem('language') || 'zh-CN'
    },
    activeTasks: new Map()
  }),

  getters: {
    isLoggedIn: state => !!state.token,
    isAdmin: state => state.user?.role === 'admin',
    activeTaskCount: state => state.activeTasks.size
  },

  actions: {
    async login(credentials) {
      try {
        const response = await axios.post('/auth/login', credentials)
        const { token, user } = response.data
        
        this.setToken(token)
        this.setUser(user)
        
        // 设置 axios 默认 Authorization header
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
        
        return response.data
      } catch (error) {
        throw new Error(error.response?.data?.message || '登录失败')
      }
    },

    loadAppConfig() {
      this.loading = true
      
      // Simulating configuration loading - replace with actual API call when ready
      setTimeout(() => {
        this.config = {
          appName: 'HappySeek',
          version: '1.0.0',
          apiUrl: import.meta.env.VITE_API_URL || '/api',
          wsUrl: import.meta.env.VITE_WS_URL || window.location.origin.replace('http', 'ws') + '/ws'
        }
        
        // Configure axios base URL
        axios.defaults.baseURL = this.config.apiUrl
        
        this.loading = false
      }, 500)
    },
    
    setWsConnected(status) {
      this.wsConnected = status
    },
    
    setOfflineMode(status) {
      this.offlineMode = status
    },

    setUser(user) {
      this.user = user
    },

    setToken(token) {
      this.token = token
      localStorage.setItem('token', token)
    },

    updateSettings(settings) {
      this.settings = { ...this.settings, ...settings }
      Object.entries(settings).forEach(([key, value]) => {
        localStorage.setItem(key, value)
      })
    },

    addTask(taskId, taskInfo) {
      this.activeTasks.set(taskId, {
        ...taskInfo,
        startTime: new Date().toISOString()
      })
    },

    updateTaskProgress(taskId, progress) {
      if (this.activeTasks.has(taskId)) {
        const task = this.activeTasks.get(taskId)
        this.activeTasks.set(taskId, {
          ...task,
          progress,
          lastUpdate: new Date().toISOString()
        })
      }
    },

    removeTask(taskId) {
      this.activeTasks.delete(taskId)
    },

    logout() {
      this.user = null
      this.token = null
      localStorage.removeItem('token')
    }
  }
})