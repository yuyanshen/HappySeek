// frontend/src/utils/socket.js
import { io } from 'socket.io-client'
import { useAppStore } from '@/stores/app'
import { useTaskStore } from '@/stores/task'

let socket = null
const RECONNECT_LIMIT = 5

export function setupTaskSocket() {
  if (socket?.connected) return
  
  const appStore = useAppStore()
  const taskStore = useTaskStore()
  
  // Get WebSocket URL from environment or app config
  const wsUrl = import.meta.env.VITE_WS_URL || 
                (appStore.config && appStore.config.wsUrl) || 
                window.location.origin.replace('http', 'ws') + '/ws'
  
  socket = io(wsUrl, {
    reconnectionAttempts: RECONNECT_LIMIT,
    timeout: 10000,
    transports: ['websocket'],
    path: '/socket.io'
  })

  socket.on('connect', () => {
    appStore.setWsConnected(true)
    console.log('WebSocket connected!')
  })

  socket.on('task_progress', (data) => {
    taskStore.updateProgress(data)
  })

  socket.on('disconnect', () => {
    appStore.setWsConnected(false)
    console.log('WebSocket disconnected')
  })

  socket.on('connect_error', (error) => {
    console.error('WebSocket connection error:', error)
    appStore.setWsConnected(false)
  })
}

export function disconnectSocket() {
  if (socket) {
    socket.disconnect()
    socket = null
    console.log('WebSocket manually disconnected')
  }
}

// Join a specific task room to receive updates for that task
export function joinTaskRoom(taskId) {
  if (socket?.connected) {
    socket.emit('join', { task_id: taskId })
  }
}

// Leave a specific task room
export function leaveTaskRoom(taskId) {
  if (socket?.connected) {
    socket.emit('leave', { task_id: taskId })
  }
}