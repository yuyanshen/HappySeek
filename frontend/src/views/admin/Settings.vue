<template>
  <div class="settings-container">
    <h2 class="settings-title">系统设置</h2>

    <!-- 设置卡片网格 -->
    <div class="settings-grid">
      <!-- 爬虫设置 -->
      <div class="settings-card glass-card fade-scale">
        <div class="card-header">
          <el-icon class="header-icon"><Connection /></el-icon>
          <h3>爬虫配置</h3>
        </div>
        <el-form :model="crawlerSettings" label-position="top">
          <el-form-item label="默认并发数">
            <el-input-number v-model="crawlerSettings.concurrency" :min="1" :max="20" />
          </el-form-item>
          <el-form-item label="请求超时(ms)">
            <el-slider
              v-model="crawlerSettings.timeout"
              :min="1000"
              :max="30000"
              :step="1000"
              show-input
            />
          </el-form-item>
          <el-form-item label="自动重试次数">
            <el-input-number v-model="crawlerSettings.retries" :min="0" :max="5" />
          </el-form-item>
          <el-form-item label="代理设置">
            <el-switch
              v-model="crawlerSettings.useProxy"
              @change="handleProxyChange"
            />
          </el-form-item>
          <el-form-item v-if="crawlerSettings.useProxy">
            <el-input
              v-model="crawlerSettings.proxyUrl"
              placeholder="http://proxy.example.com:8080"
            >
              <template #append>
                <el-button @click="testProxy">测试</el-button>
              </template>
            </el-input>
          </el-form-item>
        </el-form>
      </div>

      <!-- 系统性能 -->
      <div class="settings-card glass-card fade-scale">
        <div class="card-header">
          <el-icon class="header-icon"><CPU /></el-icon>
          <h3>性能设置</h3>
        </div>
        <el-form :model="performanceSettings" label-position="top">
          <el-form-item label="最大内存使用">
            <el-select v-model="performanceSettings.maxMemory" class="full-width">
              <el-option label="2GB" value="2048" />
              <el-option label="4GB" value="4096" />
              <el-option label="8GB" value="8192" />
            </el-select>
          </el-form-item>
          <el-form-item label="CPU限制">
            <el-slider
              v-model="performanceSettings.cpuLimit"
              :min="10"
              :max="100"
              :format-tooltip="value => `${value}%`"
            />
          </el-form-item>
          <el-form-item label="存储清理">
            <el-radio-group v-model="performanceSettings.cleanupPolicy">
              <el-radio-button label="manual">手动</el-radio-button>
              <el-radio-button label="auto">自动</el-radio-button>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="数据保留天数" v-if="performanceSettings.cleanupPolicy === 'auto'">
            <el-input-number v-model="performanceSettings.retentionDays" :min="1" :max="90" />
          </el-form-item>
        </el-form>
      </div>

      <!-- 安全设置 -->
      <div class="settings-card glass-card fade-scale">
        <div class="card-header">
          <el-icon class="header-icon"><Lock /></el-icon>
          <h3>安全设置</h3>
        </div>
        <el-form :model="securitySettings" label-position="top">
          <el-form-item label="密码策略">
            <el-select v-model="securitySettings.passwordPolicy" class="full-width">
              <el-option label="标准" value="standard" />
              <el-option label="增强" value="enhanced" />
              <el-option label="自定义" value="custom" />
            </el-select>
          </el-form-item>
          <template v-if="securitySettings.passwordPolicy === 'custom'">
            <el-form-item label="最小长度">
              <el-input-number v-model="securitySettings.minLength" :min="6" :max="20" />
            </el-form-item>
            <el-form-item label="密码要求">
              <el-checkbox-group v-model="securitySettings.requirements">
                <el-checkbox label="uppercase">大写字母</el-checkbox>
                <el-checkbox label="lowercase">小写字母</el-checkbox>
                <el-checkbox label="numbers">数字</el-checkbox>
                <el-checkbox label="special">特殊字符</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
          </template>
          <el-form-item label="登录保护">
            <el-switch
              v-model="securitySettings.loginProtection"
              @change="handleLoginProtectionChange"
            />
          </el-form-item>
          <template v-if="securitySettings.loginProtection">
            <el-form-item label="失败次数限制">
              <el-input-number v-model="securitySettings.maxAttempts" :min="3" :max="10" />
            </el-form-item>
            <el-form-item label="锁定时间(分钟)">
              <el-input-number v-model="securitySettings.lockoutDuration" :min="5" :max="60" />
            </el-form-item>
          </template>
        </el-form>
      </div>

      <!-- 通知设置 -->
      <div class="settings-card glass-card fade-scale">
        <div class="card-header">
          <el-icon class="header-icon"><Bell /></el-icon>
          <h3>通知设置</h3>
        </div>
        <el-form :model="notificationSettings" label-position="top">
          <el-form-item label="邮件通知">
            <el-switch v-model="notificationSettings.emailEnabled" />
          </el-form-item>
          <template v-if="notificationSettings.emailEnabled">
            <el-form-item label="SMTP服务器">
              <el-input v-model="notificationSettings.smtpServer" />
            </el-form-item>
            <el-form-item label="SMTP端口">
              <el-input-number v-model="notificationSettings.smtpPort" :min="1" :max="65535" />
            </el-form-item>
            <el-form-item label="发件人邮箱">
              <el-input v-model="notificationSettings.senderEmail" />
            </el-form-item>
            <el-form-item>
              <el-button @click="testEmailSettings">测试邮件配置</el-button>
            </el-form-item>
          </template>
        </el-form>
      </div>
    </div>

    <!-- 底部操作栏 -->
    <div class="settings-actions glass-card">
      <el-button @click="resetSettings">恢复默认</el-button>
      <el-button type="primary" @click="saveSettings" :loading="saving">
        保存更改
      </el-button>
    </div>

    <!-- 测试结果对话框 -->
    <el-dialog v-model="testResultVisible" :title="testResultTitle" width="400px">
      <div class="test-result" :class="testResult.status">
        <el-icon class="result-icon">
          <component :is="testResult.status === 'success' ? 'CircleCheck' : 'CircleClose'" />
        </el-icon>
        <p class="result-message">{{ testResult.message }}</p>
      </div>
      <template #footer>
        <el-button @click="testResultVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Connection,
  CPU,
  Lock,
  Bell,
  CircleCheck,
  CircleClose
} from '@element-plus/icons-vue'

// 设置状态
const crawlerSettings = reactive({
  concurrency: 5,
  timeout: 5000,
  retries: 3,
  useProxy: false,
  proxyUrl: ''
})

const performanceSettings = reactive({
  maxMemory: '4096',
  cpuLimit: 50,
  cleanupPolicy: 'manual',
  retentionDays: 30
})

const securitySettings = reactive({
  passwordPolicy: 'standard',
  minLength: 8,
  requirements: ['uppercase', 'numbers'],
  loginProtection: false,
  maxAttempts: 5,
  lockoutDuration: 30
})

const notificationSettings = reactive({
  emailEnabled: false,
  smtpServer: '',
  smtpPort: 587,
  senderEmail: ''
})

// 测试结果状态
const testResultVisible = ref(false)
const testResultTitle = ref('')
const testResult = reactive({
  status: '',
  message: ''
})

const saving = ref(false)

// 方法
const handleProxyChange = (value) => {
  if (!value) {
    crawlerSettings.proxyUrl = ''
  }
}

const handleLoginProtectionChange = (value) => {
  if (!value) {
    securitySettings.maxAttempts = 5
    securitySettings.lockoutDuration = 30
  }
}

const testProxy = async () => {
  if (!crawlerSettings.proxyUrl) {
    ElMessage.warning('请输入代理地址')
    return
  }

  testResultTitle.value = '代理测试结果'
  testResultVisible.value = true

  try {
    const response = await fetch('/api/admin/settings/test-proxy', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        proxyUrl: crawlerSettings.proxyUrl
      })
    })

    if (response.ok) {
      testResult.status = 'success'
      testResult.message = '代理服务器连接成功'
    } else {
      throw new Error('代理服务器连接失败')
    }
  } catch (error) {
    testResult.status = 'error'
    testResult.message = error.message
  }
}

const testEmailSettings = async () => {
  if (!notificationSettings.smtpServer || !notificationSettings.senderEmail) {
    ElMessage.warning('请填写完整的邮件配置')
    return
  }

  testResultTitle.value = '邮件配置测试'
  testResultVisible.value = true

  try {
    const response = await fetch('/api/admin/settings/test-email', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(notificationSettings)
    })

    if (response.ok) {
      testResult.status = 'success'
      testResult.message = '测试邮件发送成功'
    } else {
      throw new Error('测试邮件发送失败')
    }
  } catch (error) {
    testResult.status = 'error'
    testResult.message = error.message
  }
}

const resetSettings = async () => {
  try {
    const response = await fetch('/api/admin/settings/reset', {
      method: 'POST'
    })

    if (response.ok) {
      const defaults = await response.json()
      Object.assign(crawlerSettings, defaults.crawler)
      Object.assign(performanceSettings, defaults.performance)
      Object.assign(securitySettings, defaults.security)
      Object.assign(notificationSettings, defaults.notification)

      ElMessage.success('已恢复默认设置')
    } else {
      throw new Error('恢复默认设置失败')
    }
  } catch (error) {
    ElMessage.error(error.message)
  }
}

const saveSettings = async () => {
  saving.value = true

  try {
    const response = await fetch('/api/admin/settings', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        crawler: crawlerSettings,
        performance: performanceSettings,
        security: securitySettings,
        notification: notificationSettings
      })
    })

    if (response.ok) {
      ElMessage.success('设置已保存')
    } else {
      throw new Error('保存设置失败')
    }
  } catch (error) {
    ElMessage.error(error.message)
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.settings-container {
  padding: 24px;
  max-width: 1440px;
  margin: 0 auto;
}

.settings-title {
  font-size: var(--font-size-3xl);
  margin-bottom: 32px;
  background: linear-gradient(135deg, var(--primary-color), #5ac8fa);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
  margin-bottom: 24px;
}

.settings-card {
  padding: 24px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
}

.header-icon {
  font-size: 24px;
  padding: 12px;
  border-radius: var(--border-radius-md);
  background: rgba(255, 255, 255, 0.1);
}

.card-header h3 {
  margin: 0;
  font-size: var(--font-size-xl);
}

.settings-actions {
  position: sticky;
  bottom: 24px;
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  padding: 16px 24px;
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
}

.full-width {
  width: 100%;
}

/* 测试结果样式 */
.test-result {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px;
  text-align: center;
}

.result-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.test-result.success .result-icon {
  color: var(--success-color);
}

.test-result.error .result-icon {
  color: var(--error-color);
}

.result-message {
  margin: 0;
  font-size: var(--font-size-lg);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .settings-container {
    padding: 16px;
  }

  .settings-grid {
    grid-template-columns: 1fr;
  }

  .settings-actions {
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    border-radius: 0;
  }
}
</style>