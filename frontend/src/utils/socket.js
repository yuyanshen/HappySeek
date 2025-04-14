import io from 'socket.io-client'
import { useStore } from 'vuex'

let socket = null
const RECONNECT_LIMIT = 5

export function setupTaskSocket() {
  if (socket?.connected) return
  
  const store = useStore()
  
  socket = io(import.meta.env.VITE_WS_URL, {
    reconnectionAttempts: RECONNECT_LIMIT,
    timeout: 10000,
    auth: {
      token: store.state.user.token // 携带认证信息
    }
  })

  socket.on('connect', () => {
    store.commit('setWsConnected', true)
  })

  socket.on('task_update', (data) => {
    store.commit('task/updateProgress', data)
  })

  socket.on('disconnect', () => {
    store.commit('setWsConnected', false)
  })
}

export function disconnectSocket() {
  if (socket) {
    socket.disconnect()
    socket = null
  }
}