<template>
  <div class="forbidden-page">
    <div class="content">
      <h1 class="code">403</h1>
      <p class="message">抱歉，您没有访问该页面的权限</p>
      <el-space>
        <el-button type="primary" @click="$router.push('/kanban')">返回首页</el-button>
        <el-button @click="$router.back()">返回上一页</el-button>
      </el-space>
    </div>
  </div>
</template>

<script setup lang="ts">
// 403 无权限页面
</script>

<style scoped>
.forbidden-page {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
}
.content {
  text-align: center;
}
.code {
  font-size: 120px;
  color: #e74c3c;
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
