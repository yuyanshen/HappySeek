// frontend/src/stores/app.js
import { defineStore } from 'pinia'
import axios from 'axios'

export const useAppStore = defineStore('app', {
  state: () => ({
    loading: false,
    config: null,
    wsConnected: false,
    offlineMode: false
  }),

  actions: {
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
    }
  }
})