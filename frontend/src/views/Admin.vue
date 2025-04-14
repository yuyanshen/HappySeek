<!-- frontend/src/views/Admin.vue -->
<template>
    <el-container>
      <el-aside width="200px">
        <el-menu router>
          <el-submenu index="1">
            <template #title>用户管理</template>
            <el-menu-item index="/admin/users">用户列表</el-menu-item>
            <el-menu-item index="/admin/roles">角色权限</el-menu-item>
          </el-submenu>
          <el-submenu index="2">
            <template #title>爬虫管理</template>
            <el-menu-item index="/admin/tasks">任务监控</el-menu-item>
            <el-menu-item index="/admin/proxies">代理IP池</el-menu-item>
          </el-submenu>
          <el-menu-item index="/admin/logs">系统日志</el-menu-item>
        </el-menu>
      </el-aside>
      
      <el-main>
        <router-view></router-view>
        <!-- 动态仪表盘 -->
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card>
              <stat-card title="用户总数" :value="stats.users" icon="user"/>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card>
              <stat-card title="今日任务" :value="stats.tasks" icon="list"/>
            </el-card>
          </el-col>
        </el-row>
      </el-main>
    </el-container>
  </template>