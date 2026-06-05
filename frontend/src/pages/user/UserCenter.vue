<template>
  <div class="user-center-page">
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card>
          <template #header>个人信息</template>
          <el-form :model="form" label-width="100px">
            <el-form-item label="用户名">
              <el-input v-model="form.username" disabled />
            </el-form-item>
            <el-form-item label="昵称">
              <el-input v-model="form.nickname" />
            </el-form-item>
            <el-form-item label="邮箱">
              <el-input v-model="form.email" />
            </el-form-item>
            <el-form-item label="手机号">
              <el-input v-model="form.phone" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary">保存</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>头像设置</template>
          <div class="avatar-section">
            <el-avatar :size="120" :src="form.avatar_url" />
            <div class="avatar-actions">
              <el-button size="small" @click="handleUpload">更换头像</el-button>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>微信绑定</template>
          <div v-if="!form.wechat_bound">
            <el-button type="success" @click="handleBindWechat">绑定微信</el-button>
          </div>
          <div v-else>
            <el-tag type="success">已绑定</el-tag>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'

const form = reactive({
  username: 'test_user',
  nickname: '测试用户',
  email: 'test@example.com',
  phone: '',
  avatar_url: '',
  wechat_bound: false,
})

function handleUpload() {
  // TODO: 打开文件选择器
}

function handleBindWechat() {
  // TODO: 打开微信绑定
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
</style>
