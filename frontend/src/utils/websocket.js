import { io } from 'socket.io-client'
import { useAppStore } from '@/stores/app'

class WebSocketService {
  constructor() {
    this.socket = null
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
  }

  connect() {
    const store = useAppStore()
    const wsUrl = store.config?.wsUrl

    if (!wsUrl) {
      console.error('WebSocket URL not configured')
      return
    }

    this.socket = io(wsUrl, {
      transports: ['websocket'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: this.maxReconnectAttempts
    })

    this.socket.on('connect', () => {
      console.log('WebSocket connected')
      store.setWsConnected(true)
      this.reconnectAttempts = 0
    })

    this.socket.on('disconnect', () => {
      console.log('WebSocket disconnected')
      store.setWsConnected(false)
    })

    this.socket.on('task_update', ({ taskId, status, progress }) => {
      if (status === 'completed' || status === 'failed') {
        store.removeTask(taskId)
      } else {
        store.updateTaskProgress(taskId, progress)
      }
    })

    this.socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error)
      this.reconnectAttempts++
      
      if (this.reconnectAttempts >= this.maxReconnectAttempts) {
        store.setOfflineMode(true)
      }
    })
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
    }
  }

  subscribe(taskId) {
    if (this.socket) {
      this.socket.emit('subscribe', { taskId })
    }
  }

  unsubscribe(taskId) {
    if (this.socket) {
      this.socket.emit('unsubscribe', { taskId })
    }
  }
}

export default new WebSocketService()