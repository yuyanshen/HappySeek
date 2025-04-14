export default {
    namespaced: true,
    state: () => ({
      activeTasks: [],
      pendingTasks: []
    }),
    mutations: {
      ADD_TASK(state, task) {
        if (state.activeTasks.length < 10) {
          state.activeTasks.push({
            ...task,
            progress: 0,
            status: 'waiting',
            logs: []
          })
        } else {
          state.pendingTasks.push(task)
        }
      },
      UPDATE_PROGRESS(state, { taskId, ...update }) {
        const task = state.activeTasks.find(t => t.id === taskId)
        if (task) {
          Object.assign(task, update)
          if (update.log) {
            task.logs.push(update.log)
          }
          
          // 任务完成时从队列移除
          if (update.status === 'completed' || update.status === 'failed') {
            setTimeout(() => {
              state.activeTasks = state.activeTasks.filter(t => t.id !== taskId)
              if (state.pendingTasks.length > 0) {
                this.commit('task/PROMOTE_PENDING')
              }
            }, 3000)
          }
        }
      },
      PROMOTE_PENDING(state) {
        if (state.activeTasks.length < 10 && state.pendingTasks.length > 0) {
          const task = state.pendingTasks.shift()
          state.activeTasks.push({
            ...task,
            progress: 0,
            status: 'waiting',
            logs: []
          })
        }
      }
    }
  }