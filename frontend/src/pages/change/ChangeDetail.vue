<template>
  <div class="change-detail-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>变更详情</span>
          <el-button @click="router.back()">返回</el-button>
        </div>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="变更 ID">chg_001</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag>草稿</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="变更类型">DB 变更</el-descriptions-item>
        <el-descriptions-item label="变更原因">需求变更</el-descriptions-item>
        <el-descriptions-item label="变更内容" :span="2">
          <div class="content-text">示例变更内容描述...</div>
        </el-descriptions-item>
        <el-descriptions-item label="影响范围" :span="2">
          无
        </el-descriptions-item>
        <el-descriptions-item label="关联需求号">无</el-descriptions-item>
        <el-descriptions-item label="创建人">test_user</el-descriptions-item>
      </el-descriptions>
      <div class="action-bar">
        <el-button type="primary">审批通过</el-button>
        <el-button type="danger">驳回</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
const router = useRouter()
</script>

<style scoped>
.change-detail-page {
  padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.content-text {
  white-space: pre-wrap;
}
.action-bar {
  margin-top: 16px;
  text-align: right;
}
</style>
