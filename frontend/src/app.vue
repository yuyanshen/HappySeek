import { setupTaskSocket } from '@/utils/socket'

export default {
  setup() {
    onMounted(() => {
      setupTaskSocket()
    })
  }
}
<template>
    <el-config-provider :locale="locale">
      <router-view v-slot="{ Component }">
        <component :is="Component" :class="{ 'mobile-layout': isMobile }" />
      </router-view>
    </el-config-provider>
  </template>
  
  <script>
  import { computed } from 'vue'
  import { useStore } from 'vuex'
  import { ElConfigProvider } from 'element-plus'
  import zhLocale from 'element-plus/lib/locale/lang/zh-cn'
  
  export default {
    components: { ElConfigProvider },
    setup() {
      const store = useStore()
      const isMobile = computed(() => store.state.app.isMobile)
      
      return {
        locale: zhLocale,
        isMobile
      }
    }
  }
  </script>
  
  <style>
  .mobile-layout {
    padding: 10px;
    
    .el-card {
      margin-bottom: 10px;
    }
    
    .el-form-item__label {
      width: 100% !important;
    }
  }
  </style>