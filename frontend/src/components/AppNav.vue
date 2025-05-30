<!-- frontend/src/components/AppNav.vue -->
<template>
  <nav class="app-nav" :class="{ 'nav-collapsed': isCollapsed }">
    <div class="nav-header glass-card">
      <div class="logo-container">
        <img src="/logo.svg" alt="HappySeek" class="nav-logo" />
        <span class="logo-text" v-show="!isCollapsed">HappySeek</span>
      </div>
      <el-button class="collapse-btn" :icon="isCollapsed ? Expand : Fold" @click="toggleCollapse" />
    </div>

    <el-scrollbar>
      <el-menu
        :default-active="activeRoute"
        :collapse="isCollapsed"
        class="nav-menu"
        @select="handleSelect"
      >
        <template v-for="item in navItems">
          <el-menu-item v-if="!item.children && (!item.requireAdmin || isAdmin)" :index="item.path" class="fade-slide-item">
            <el-icon><component :is="item.icon" /></el-icon>
            <template #title>
              <span class="nav-item-title">{{ item.title }}</span>
            </template>
          </el-menu-item>
          <el-sub-menu v-else-if="item.children && (!item.requireAdmin || isAdmin)" :index="item.path" class="fade-slide-item">
            <template #title>
              <el-icon><component :is="item.icon" /></el-icon>
              <span class="nav-item-title">{{ item.title }}</span>
            </template>
            <el-menu-item v-for="subItem in item.children" :key="subItem.path" :index="subItem.path" class="sub-item">
              <el-icon><component :is="subItem.icon" /></el-icon>
              {{ subItem.title }}
            </el-menu-item>
          </el-sub-menu>
        </template>
      </el-menu>
    </el-scrollbar>

    <div class="nav-footer glass-card" v-show="!isCollapsed">
      <el-dropdown trigger="click">
        <div class="user-info">
          <el-avatar :size="32" :src="userAvatar" />
          <div class="user-details" v-if="!isCollapsed">
            <span class="username">{{ userName }}</span>
            <span class="role">{{ userRole }}</span>
          </div>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item @click="navigateTo('/profile')">
              <el-icon><User /></el-icon>个人设置
            </el-dropdown-item>
            <el-dropdown-item divided @click="handleLogout">
              <el-icon><Switch /></el-icon>退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </nav>
</template>

<script setup>
import { useAppStore } from '@/stores/app'
import { Connection, Expand, Fold, List, Monitor, Setting, Switch, User } from '@element-plus/icons-vue'
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()
const isCollapsed = ref(false)

const navItems = [
  { path: '/dashboard', title: '仪表盘', icon: Monitor },
  { path: '/crawler', title: '爬虫配置', icon: Connection },
  { path: '/task-monitor', title: '任务监控', icon: List },
  {
    path: '/admin',
    title: '系统管理',
    icon: Setting,
    children: [
      { path: '/admin/monitor', title: '服务监控', icon: Monitor },
      { path: '/admin/settings', title: '系统设置', icon: Setting },
      { path: '/admin/users', title: '用户管理', icon: User }
    ],
    requireAdmin: true
  }
]

const activeRoute = computed(() => route.path)
const isAdmin = computed(() => appStore.userRole === 'admin')

const userName = computed(() => appStore.userName || '未登录')
const userRole = computed(() => appStore.userRole === 'admin' ? '管理员' : '普通用户')
const userAvatar = computed(() => appStore.userAvatar || '/default-avatar.png')

const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
}

const handleSelect = (path) => {
  router.push(path)
}

const navigateTo = (path) => {
  router.push(path)
}

const handleLogout = () => {
  appStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.app-nav {
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  width: 240px;
  display: flex;
  flex-direction: column;
  background: var(--surface-color);
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  transition: width var(--transition-normal);
  z-index: var(--z-index-fixed);
}

.nav-collapsed {
  width: 64px;
}

.nav-header {
  padding: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-radius: 0;
  border: none;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 12px;
  overflow: hidden;
}

.nav-logo {
  width: 32px;
  height: 32px;
  flex-shrink: 0;
}

.logo-text {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  background: linear-gradient(135deg, var(--primary-color), #5ac8fa);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  white-space: nowrap;
}

.collapse-btn {
  padding: 6px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  transition: color var(--transition-fast);
}

.collapse-btn:hover {
  color: var(--text-primary);
}

.nav-menu {
  flex: 1;
  border: none;
  background: transparent;
}

.fade-slide-item {
  animation: fadeSlideIn 0.3s ease-out;
  animation-fill-mode: both;
}

.nav-item-title {
  margin-left: 8px;
}

.sub-item {
  padding-left: 46px !important;
}

.nav-footer {
  padding: 16px;
  border-radius: 0;
  border: none;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  padding: 4px;
  border-radius: var(--border-radius-md);
  transition: background-color var(--transition-fast);
}

.user-info:hover {
  background: rgba(255, 255, 255, 0.05);
}

.user-details {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.username {
  font-weight: var(--font-weight-medium);
  color: var(--text-primary);
}

.role {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

@keyframes fadeSlideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .app-nav {
    transform: translateX(-100%);
    width: 240px !important;
  }

  .app-nav.nav-visible {
    transform: translateX(0);
  }

  .nav-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(4px);
    z-index: calc(var(--z-index-fixed) - 1);
  }
}
</style>