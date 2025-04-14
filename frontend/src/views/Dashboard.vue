<template>
    <div class="dashboard">
      <el-row :gutter="20">
        <el-col :span="8">
          <data-card 
            title="任务统计" 
            type="pie"
            :data="taskStats"
          />
        </el-col>
        <el-col :span="16">
          <data-card
            title="爬取趋势"
            type="line"
            :data="trendData"
          />
        </el-col>
      </el-row>
      
      <el-tabs>
        <el-tab-pane label="实时监控">
          <task-monitor :tasks="activeTasks" />
        </el-tab-pane>
        <el-tab-pane label="异常检测">
          <anomaly-detection :logs="errorLogs" />
        </el-tab-pane>
      </el-tabs>
    </div>
  </template>
  
  <script>
  import { ref, onMounted } from 'vue'
  import { useStore } from 'vuex'
  
  export default {
    setup() {
      const store = useStore()
      const loading = ref(true)
      
      const fetchData = async () => {
        await Promise.all([
          store.dispatch('fetchTaskStats'),
          store.dispatch('fetchTrendData'),
          store.dispatch('fetchActiveTasks')
        ])
        loading.value = false
      }
      
      onMounted(fetchData)
      
      return {
        loading,
        taskStats: computed(() => store.state.dashboard.taskStats),
        trendData: computed(() => store.state.dashboard.trendData),
        activeTasks: computed(() => store.state.tasks.active),
        errorLogs: computed(() => store.state.logs.errors)
      }
    }
  }
  </script>