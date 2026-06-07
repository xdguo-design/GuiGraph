<template>
  <div class="user-center-page">
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card>
          <template #header>个人信息</template>
          <el-form :model="form" label-width="100px" v-loading="loading">
            <el-form-item label="用户名">
              <el-input v-model="form.username" disabled />
            </el-form-item>
            <el-form-item label="昵称">
              <el-input v-model="form.nickname" placeholder="请输入昵称" />
            </el-form-item>
            <el-form-item label="邮箱">
              <el-input v-model="form.email" placeholder="请输入邮箱" />
            </el-form-item>
            <el-form-item label="手机号">
              <el-input v-model="form.phone" placeholder="请输入手机号" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
              <el-button @click="loadUserInfo">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>头像设置</template>
          <div class="avatar-section">
            <el-avatar :size="120" :src="form.avatar_url">
              {{ form.username?.charAt(0)?.toUpperCase() }}
            </el-avatar>
            <div class="avatar-actions">
              <input
                ref="fileInput"
                type="file"
                accept="image/jpeg,image/png,image/gif,image/webp"
                style="display: none"
                @change="onFileChange"
              />
              <el-button size="small" type="primary" :loading="uploading" @click="pickFile">更换头像</el-button>
              <div class="tip">支持 JPG/PNG/GIF/WebP，最大 2MB</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>微信绑定</template>
          <div v-loading="wechatLoading">
            <div v-if="form.wechat_bound" class="wechat-bound">
              <el-tag type="success" size="large">已绑定</el-tag>
              <div class="openid">OpenID: {{ form.wechat_openid }}</div>
              <el-button size="small" type="danger" plain @click="handleUnbindWechat">解绑</el-button>
            </div>
            <div v-else>
              <el-button type="success" @click="openBindDialog" :loading="binding">
                绑定微信
              </el-button>
              <div class="tip">绑定后可用微信扫码登录</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 微信绑定对话框 -->
    <el-dialog v-model="bindDialogVisible" title="绑定微信" width="480px">
      <div v-if="wechatQr.mode === 'dev'">
        <el-alert :title="wechatQr.tip" type="info" :closable="false" show-icon />
        <el-form style="margin-top: 16px">
          <el-form-item label="授权码">
            <el-input v-model="wechatCode" placeholder="dev 模式：任意 4 位以上字符串" />
          </el-form-item>
        </el-form>
      </div>
      <div v-else>
        <el-alert :title="wechatQr.tip" type="info" :closable="false" show-icon />
        <div v-if="wechatQr.qr_url" class="qrcode">
          <img :src="wechatQr.qr_url" alt="wechat qrcode" style="max-width: 240px" />
        </div>
      </div>
      <template #footer>
        <el-button @click="bindDialogVisible = false">取消</el-button>
        <el-button v-if="wechatQr.mode === 'dev'" type="primary" :loading="binding" @click="handleBindWechat">确认绑定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { userAPI } from '@/api/user'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const form = reactive({
  username: '',
  nickname: '',
  email: '',
  phone: '',
  avatar_url: '',
  wechat_bound: false,
  wechat_openid: '',
})

const loading = ref(false)
const saving = ref(false)
const uploading = ref(false)
const binding = ref(false)
const wechatLoading = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)
const bindDialogVisible = ref(false)
const wechatCode = ref('')
const wechatQr = reactive<{ mode: string; tip: string; qr_url: string }>({
  mode: 'dev',
  tip: '',
  qr_url: '',
})

onMounted(async () => {
  await loadUserInfo()
})

async function loadUserInfo() {
  loading.value = true
  try {
    const data: any = await userAPI.getProfile()
    Object.assign(form, data)
  } catch (error: any) {
    ElMessage.error(error?.message || '加载用户信息失败')
  } finally {
    loading.value = false
  }
}

async function handleSave() {
  saving.value = true
  try {
    await userAPI.updateProfile({
      nickname: form.nickname,
      email: form.email,
      phone: form.phone,
    })
    ElMessage.success('保存成功')
  } catch (error: any) {
    ElMessage.error(error?.message || '保存失败')
  } finally {
    saving.value = false
  }
}

function pickFile() {
  fileInput.value?.click()
}

async function onFileChange(e: Event) {
  const target = e.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  if (file.size > 2 * 1024 * 1024) {
    ElMessage.error('头像文件不能超过 2MB')
    target.value = ''
    return
  }
  uploading.value = true
  try {
    const res: any = await userAPI.uploadAvatar(file)
    form.avatar_url = res.avatar_url
    // 同步到全局 auth store，刷新右上角头像
    if (authStore.userInfo) {
      authStore.setUserInfo({ ...authStore.userInfo, avatar_url: res.avatar_url })
    }
    ElMessage.success(res.message || '头像上传成功')
  } catch (error: any) {
    ElMessage.error(error?.message || '头像上传失败')
  } finally {
    uploading.value = false
    target.value = ''
  }
}

async function openBindDialog() {
  bindDialogVisible.value = true
  wechatCode.value = ''
  wechatLoading.value = true
  try {
    const res: any = await userAPI.getWechatQrCode()
    wechatQr.mode = res.mode
    wechatQr.tip = res.tip
    wechatQr.qr_url = res.qr_url
    if (res.mode === 'dev' && !wechatCode.value) {
      // 自动填一个示例
      wechatCode.value = 'dev-' + Math.random().toString(36).substring(2, 8)
    }
  } catch (e) {
    wechatQr.mode = 'dev'
    wechatQr.tip = '开发模式：输入任意 4 位以上字符串即可'
  } finally {
    wechatLoading.value = false
  }
}

async function handleBindWechat() {
  if (!wechatCode.value || wechatCode.value.length < 4) {
    ElMessage.warning('请输入至少 4 位的授权码')
    return
  }
  binding.value = true
  try {
    const res: any = await userAPI.bindWechat(wechatCode.value)
    ElMessage.success(res.message || '微信绑定成功')
    form.wechat_bound = true
    form.wechat_openid = res.openid
    bindDialogVisible.value = false
  } catch (error: any) {
    ElMessage.error(error?.message || '绑定失败')
  } finally {
    binding.value = false
  }
}

async function handleUnbindWechat() {
  try {
    await ElMessageBox.confirm('确定要解绑微信吗？', '提示', {
      type: 'warning',
      confirmButtonText: '解绑',
      cancelButtonText: '取消',
    })
  } catch {
    return
  }
  binding.value = true
  try {
    await userAPI.unbindWechat()
    form.wechat_bound = false
    form.wechat_openid = ''
    ElMessage.success('已解绑微信')
  } catch (error: any) {
    ElMessage.error(error?.message || '解绑失败')
  } finally {
    binding.value = false
  }
}
</script>

<style scoped>
.user-center-page {
  padding: 20px;
}
.avatar-section {
  text-align: center;
}
.avatar-actions {
  margin-top: 16px;
}
.tip {
  margin-top: 8px;
  color: #909399;
  font-size: 12px;
}
.wechat-bound {
  text-align: center;
}
.openid {
  margin: 12px 0;
  font-size: 12px;
  color: #909399;
  word-break: break-all;
}
.qrcode {
  text-align: center;
  margin-top: 16px;
}
</style>
