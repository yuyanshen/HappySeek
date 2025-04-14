// frontend/src/stores/task.js
import { defineStore } from 'pinia'

export const useTaskStore = defineStore('task', {
  state: () => ({
    activeTasks: [],
    pendingTasks: []
  }),

  actions: {
    addTask(task) {
      if (this.activeTasks.length < 10) {
        this.activeTasks.push({
          ...task,
          progress: 0,
          status: 'waiting',
          logs: []
        })
      } else {
        this.pendingTasks.push(task)
      }
    },
    
    updateProgress({ taskId, ...update }) {
      const task = this.activeTasks.find(t => t.id === taskId)
      if (task) {
        Object.assign(task, update)
        if (update.log) {
          task.logs.push(update.log)
        }
        
        // Remove task from queue when completed
        if (update.status === 'completed' || update.status === 'failed') {
          setTimeout(() => {
            this.activeTasks = this.activeTasks.filter(t => t.id !== taskId)
            if (this.pendingTasks.length > 0) {
              this.promotePending()
            }
          }, 3000)
        }
      }
    },
    
    promotePending() {
      if (this.activeTasks.length < 10 && this.pendingTasks.length > 0) {
        const task = this.pendingTasks.shift()
        this.activeTasks.push({
          ...task,
          progress: 0,
          status: 'waiting',
          logs: []
        })
      }
    }
  }
})