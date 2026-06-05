<template>
  <div class="organization-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>组织架构</span>
          <el-button type="primary" @click="handleAdd">新建</el-button>
        </div>
      </template>
      <el-empty description="暂无组织数据" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
function handleAdd() {
  // TODO: 打开新建对话框
}
</script>

<style scoped>
.organization-page {
  padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
