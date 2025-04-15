<template>
  <div class="users-container">
    <!-- 顶部操作栏 -->
    <div class="top-bar glass-card fade-scale">
      <div class="search-section">
        <el-input
          v-model="searchQuery"
          placeholder="搜索用户..."
          :prefix-icon="Search"
          clearable
        />
        <el-select v-model="filterRole" placeholder="角色筛选" clearable>
          <el-option label="管理员" value="admin" />
          <el-option label="普通用户" value="user" />
        </el-select>
      </div>
      <el-button type="primary" @click="handleAddUser" :icon="Plus">
        添加用户
      </el-button>
    </div>

    <!-- 用户列表 -->
    <div class="users-grid fade-scale">
      <div v-for="user in filteredUsers" :key="user.id" class="user-card glass-card">
        <div class="user-header">
          <div class="user-avatar" :style="{ backgroundColor: getAvatarColor(user.username) }">
            {{ user.username.charAt(0).toUpperCase() }}
          </div>
          <div class="user-info">
            <h3>{{ user.username }}</h3>
            <p class="user-email">{{ user.email }}</p>
          </div>
          <el-dropdown trigger="click" class="user-actions">
            <el-icon class="more-icon"><More /></el-icon>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="handleEditUser(user)">
                  <el-icon><Edit /></el-icon> 编辑
                </el-dropdown-item>
                <el-dropdown-item @click="handleResetPassword(user)" v-if="user.role !== 'admin'">
                  <el-icon><Key /></el-icon> 重置密码
                </el-dropdown-item>
                <el-dropdown-item divided type="danger" @click="handleDeleteUser(user)" v-if="user.role !== 'admin'">
                  <el-icon><Delete /></el-icon> 删除
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
        
        <div class="user-body">
          <div class="user-stats">
            <div class="stat-item">
              <span class="stat-label">角色</span>
              <el-tag :type="user.role === 'admin' ? 'danger' : 'success'" size="small">
                {{ user.role === 'admin' ? '管理员' : '普通用户' }}
              </el-tag>
            </div>
            <div class="stat-item">
              <span class="stat-label">部门</span>
              <span class="stat-value">{{ user.department || '未分配' }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">最后登录</span>
              <span class="stat-value">{{ formatDate(user.last_login) }}</span>
            </div>
          </div>

          <div class="user-meta">
            <div class="meta-item">
              <el-icon><Calendar /></el-icon>
              <span>创建于 {{ formatDate(user.created_at) }}</span>
            </div>
            <div class="meta-item">
              <el-icon><Timer /></el-icon>
              <span>{{ user.active ? '活跃' : '非活跃' }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 用户表单对话框 -->
    <el-dialog
      :title="dialogTitle"
      v-model="dialogVisible"
      width="500px"
      class="user-dialog"
    >
      <el-form
        ref="userFormRef"
        :model="userForm"
        :rules="userRules"
        label-position="top"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" type="email" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!userForm.id">
          <el-input v-model="userForm.password" type="password" show-password />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="userForm.role" class="full-width">
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="user" />
          </el-select>
        </el-form-item>
        <el-form-item label="部门" prop="department">
          <el-select v-model="userForm.department" class="full-width">
            <el-option v-for="dept in departments" :key="dept.id" :label="dept.name" :value="dept.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmitUser" :loading="submitting">
            确认
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus, Edit, Delete, More, Calendar, Timer, Key } from '@element-plus/icons-vue'

// 状态
const searchQuery = ref('')
const filterRole = ref('')
const dialogVisible = ref(false)
const dialogTitle = ref('')
const submitting = ref(false)
const userFormRef = ref(null)
const users = ref([])
const departments = ref([])

const userForm = reactive({
  id: null,
  username: '',
  email: '',
  password: '',
  role: 'user',
  department: null
})

// 表单验证规则
const userRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能小于6个字符', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择用户角色', trigger: 'change' }
  ]
}

// 计算属性
const filteredUsers = computed(() => {
  return users.value.filter(user => {
    const matchQuery = !searchQuery.value ||
      user.username.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      user.email.toLowerCase().includes(searchQuery.value.toLowerCase())
    
    const matchRole = !filterRole.value || user.role === filterRole.value
    
    return matchQuery && matchRole
  })
})

// 方法
const getAvatarColor = (username) => {
  const colors = [
    '#1abc9c', '#2ecc71', '#3498db', '#9b59b6', '#34495e',
    '#16a085', '#27ae60', '#2980b9', '#8e44ad', '#2c3e50'
  ]
  const index = username.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0) % colors.length
  return colors[index]
}

const formatDate = (date) => {
  if (!date) return '未知'
  return new Date(date).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 用户操作
const handleAddUser = () => {
  dialogTitle.value = '添加用户'
  userForm.id = null
  userForm.username = ''
  userForm.email = ''
  userForm.password = ''
  userForm.role = 'user'
  userForm.department = null
  dialogVisible.value = true
}

const handleEditUser = (user) => {
  dialogTitle.value = '编辑用户'
  Object.assign(userForm, user)
  dialogVisible.value = true
}

const handleDeleteUser = async (user) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${user.username}" 吗？`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const response = await fetch(`/api/admin/users/${user.id}`, {
      method: 'DELETE'
    })
    
    if (response.ok) {
      ElMessage.success('删除成功')
      await fetchUsers()
    } else {
      throw new Error('删除失败')
    }
  } catch (error) {
    if (error.message !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

const handleResetPassword = async (user) => {
  try {
    await ElMessageBox.confirm(
      `确定要重置 "${user.username}" 的密码吗？`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const response = await fetch(`/api/admin/users/${user.id}/reset-password`, {
      method: 'POST'
    })
    
    if (response.ok) {
      const { password } = await response.json()
      ElMessageBox.alert(
        `新密码: ${password}`,
        '密码重置成功',
        {
          confirmButtonText: '复制密码',
          callback: () => {
            navigator.clipboard.writeText(password)
            ElMessage.success('密码已复制到剪贴板')
          }
        }
      )
    } else {
      throw new Error('重置密码失败')
    }
  } catch (error) {
    if (error.message !== 'cancel') {
      ElMessage.error(error.message || '重置密码失败')
    }
  }
}

const handleSubmitUser = async () => {
  if (!userFormRef.value) return
  
  try {
    await userFormRef.value.validate()
    submitting.value = true
    
    const method = userForm.id ? 'PUT' : 'POST'
    const url = userForm.id ? `/api/admin/users/${userForm.id}` : '/api/admin/users'
    
    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(userForm)
    })
    
    if (response.ok) {
      ElMessage.success(userForm.id ? '更新成功' : '添加成功')
      dialogVisible.value = false
      await fetchUsers()
    } else {
      throw new Error(userForm.id ? '更新失败' : '添加失败')
    }
  } catch (error) {
    ElMessage.error(error.message || (userForm.id ? '更新失败' : '添加失败'))
  } finally {
    submitting.value = false
  }
}

// 数据获取
const fetchUsers = async () => {
  try {
    const response = await fetch('/api/admin/users')
    users.value = await response.json()
  } catch (error) {
    ElMessage.error('获取用户列表失败')
  }
}

const fetchDepartments = async () => {
  try {
    const response = await fetch('/api/admin/departments')
    departments.value = await response.json()
  } catch (error) {
    ElMessage.error('获取部门列表失败')
  }
}

// 生命周期钩子
onMounted(() => {
  fetchUsers()
  fetchDepartments()
})
</script>

<style scoped>
.users-container {
  padding: 24px;
  max-width: 1440px;
  margin: 0 auto;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  margin-bottom: 24px;
}

.search-section {
  display: flex;
  gap: 16px;
  flex: 1;
  max-width: 600px;
}

.users-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}

.user-card {
  overflow: hidden;
}

.user-header {
  display: flex;
  align-items: center;
  padding: 20px;
  background: rgba(255, 255, 255, 0.02);
}

.user-avatar {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 600;
  color: white;
  margin-right: 16px;
}

.user-info {
  flex: 1;
}

.user-info h3 {
  margin: 0;
  font-size: var(--font-size-lg);
}

.user-email {
  margin: 4px 0 0;
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
}

.user-actions {
  padding: 8px;
}

.more-icon {
  font-size: 20px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: var(--transition-fast);
}

.more-icon:hover {
  color: var(--text-primary);
}

.user-body {
  padding: 20px;
}

.user-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.stat-item {
  text-align: center;
}

.stat-label {
  display: block;
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  margin-bottom: 8px;
}

.stat-value {
  font-weight: 500;
}

.user-meta {
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  margin-bottom: 8px;
}

.meta-item .el-icon {
  font-size: 16px;
}

.full-width {
  width: 100%;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .users-container {
    padding: 16px;
  }

  .top-bar {
    flex-direction: column;
    gap: 16px;
  }

  .search-section {
    width: 100%;
    max-width: none;
  }

  .el-button {
    width: 100%;
  }

  .users-grid {
    grid-template-columns: 1fr;
  }
}
</style>