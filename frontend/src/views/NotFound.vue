<!-- frontend/src/views/NotFound.vue -->
<template>
  <div class="not-found-container">
    <div class="content-wrapper glass-card fade-scale">
      <div class="illustration">
        <svg class="error-icon" viewBox="0 0 128 128">
          <path d="M64 0C28.7 0 0 28.7 0 64s28.7 64 64 64 64-28.7 64-64S99.3 0 64 0zm0 96c-4.4 0-8-3.6-8-8s3.6-8 8-8 8 3.6 8 8-3.6 8-8 8zm8-32c0 4.4-3.6 8-8 8s-8-3.6-8-8V32c0-4.4 3.6-8 8-8s8 3.6 8 8v32z" fill="currentColor"/>
        </svg>
      </div>
      
      <h1 class="error-title">页面未找到</h1>
      <p class="error-message">抱歉，您访问的页面不存在或已被移除。</p>
      
      <div class="action-buttons">
        <el-button @click="$router.go(-1)">返回上一页</el-button>
        <el-button type="primary" @click="$router.push('/')">
          返回首页
        </el-button>
      </div>

      <div class="help-section">
        <h3>您可以尝试：</h3>
        <ul>
          <li>检查输入的网址是否正确</li>
          <li>清除浏览器缓存后重试</li>
          <li>通过导航菜单访问其他页面</li>
        </ul>
      </div>

      <!-- 漂浮元素装饰 -->
      <div class="floating-elements">
        <div class="floating-circle circle-1"></div>
        <div class="floating-circle circle-2"></div>
        <div class="floating-circle circle-3"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.not-found-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  background: linear-gradient(135deg, var(--background-color), var(--surface-color));
  position: relative;
  overflow: hidden;
}

.content-wrapper {
  max-width: 600px;
  width: 100%;
  padding: 48px;
  text-align: center;
  position: relative;
  z-index: 1;
}

.illustration {
  margin-bottom: 32px;
}

.error-icon {
  width: 128px;
  height: 128px;
  color: var(--primary-color);
  opacity: 0.8;
}

.error-title {
  font-size: var(--font-size-4xl);
  margin: 0 0 16px;
  background: linear-gradient(135deg, var(--primary-color), #5ac8fa);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.error-message {
  font-size: var(--font-size-lg);
  color: var(--text-secondary);
  margin: 0 0 32px;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-bottom: 40px;
}

.help-section {
  text-align: left;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding-top: 24px;
}

.help-section h3 {
  font-size: var(--font-size-lg);
  margin: 0 0 16px;
  color: var(--text-secondary);
}

.help-section ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.help-section li {
  position: relative;
  padding-left: 24px;
  margin-bottom: 12px;
  color: var(--text-secondary);
}

.help-section li::before {
  content: "•";
  position: absolute;
  left: 8px;
  color: var(--primary-color);
}

/* 漂浮元素动画 */
.floating-elements {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.floating-circle {
  position: absolute;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-color), #5ac8fa);
  opacity: 0.1;
}

.circle-1 {
  width: 200px;
  height: 200px;
  top: -100px;
  right: -100px;
  animation: float 20s infinite;
}

.circle-2 {
  width: 150px;
  height: 150px;
  bottom: -75px;
  left: -75px;
  animation: float 15s infinite reverse;
}

.circle-3 {
  width: 100px;
  height: 100px;
  top: 50%;
  right: 10%;
  animation: float 18s infinite;
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0);
  }
  25% {
    transform: translate(50px, -50px);
  }
  50% {
    transform: translate(0, -100px);
  }
  75% {
    transform: translate(-50px, -50px);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .content-wrapper {
    padding: 32px 20px;
  }

  .error-title {
    font-size: var(--font-size-3xl);
  }

  .error-message {
    font-size: var(--font-size-base);
  }

  .action-buttons {
    flex-direction: column;
  }

  .el-button {
    width: 100%;
  }
}
</style>