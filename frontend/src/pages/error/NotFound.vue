<template>
  <div class="not-found-page">
    <div class="content">
      <h1 class="code">404</h1>
      <p class="message">您访问的页面不存在</p>
      <el-space>
        <el-button type="primary" @click="$router.push('/kanban')">返回首页</el-button>
        <el-button @click="$router.back()">返回上一页</el-button>
      </el-space>
    </div>
  </div>
</template>

<script setup lang="ts">
// 404 页面
</script>

<style scoped>
.not-found-page {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--theme-bg, #f5f7fa);
}
.content {
  text-align: center;
}
.code {
  font-size: 120px;
  color: #1a5276;
  font-weight: 700;
  margin: 0;
  line-height: 1;
}
.message {
  font-size: 18px;
  color: #7f8c8d;
  margin: 20px 0 32px;
}
</style>
