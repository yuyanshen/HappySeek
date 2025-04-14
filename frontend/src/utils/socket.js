import io from 'socket.io-client'
import { useStore } from 'vuex'

const socket = io('http://localhost:5000')

export function setupTaskSocket() {
  const store = useStore()
  
  socket.on('task_progress', (data) => {
    store.commit('task/UPDATE_PROGRESS', {
      taskId: data.task_id,
      progress: data.progress,
      status: data.status,
      log: {
        time: new Date(data.timestamp).toLocaleTimeString(),
        message: data.message
      }
    })
  })
}