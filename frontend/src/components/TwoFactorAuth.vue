<!-- 双因素认证组件 -->
<template>
  <div class="two-factor-auth">
    <el-dialog
      v-model="visible"
      title="双因素认证"
      width="400px"
      :close-on-click-modal="false"
    >
      <template v-if="setupMode">
        <div class="setup-2fa">
          <h3>扫描二维码</h3>
          <img :src="qrCodeUrl" alt="2FA QR Code" class="qr-code" />
          <p>或者输入密钥：</p>
          <el-input v-model="secret" readonly class="secret-key" />
          <p class="hint">
            请使用Google Authenticator或其他2FA应用扫描二维码
          </p>
        </div>
      </template>
      <template v-else>
        <el-form :model="form" @submit.prevent="verify">
          <el-form-item label="验证码">
            <el-input
              v-model="form.code"
              maxlength="6"
              placeholder="请输入6位验证码"
              autocomplete="off"
            >
              <template #prefix>
                <el-icon><Key /></el-icon>
              </template>
            </el-input>
          </el-form-item>
        </el-form>
      </template>

      <template #footer>
        <el-button @click="onCancel">取消</el-button>
        <el-button type="primary" @click="onConfirm">
          {{ setupMode ? '完成设置' : '验证' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, defineEmits, defineProps } from 'vue'
import { ElMessage } from 'element-plus'
import { Key } from '@element-plus/icons-vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  setupMode: {
    type: Boolean,
    default: false
  },
  qrCodeUrl: {
    type: String,
    default: ''
  },
  secret: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:visible', 'verify', 'cancel'])

const form = ref({
  code: ''
})

const onConfirm = () => {
  if (!form.value.code && !props.setupMode) {
    ElMessage.warning('请输入验证码')
    return
  }
  emit('verify', form.value.code)
}

const onCancel = () => {
  form.value.code = ''
  emit('cancel')
  emit('update:visible', false)
}
</script>

<style scoped>
.two-factor-auth {
  .setup-2fa {
    text-align: center;
    
    .qr-code {
      width: 200px;
      height: 200px;
      margin: 20px 0;
    }
    
    .secret-key {
      width: 80%;
      margin: 10px auto;
    }
    
    .hint {
      color: #666;
      font-size: 14px;
      margin-top: 10px;
    }
  }
}
</style>