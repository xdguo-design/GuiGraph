<template>
  <div class="dashboard-page">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card>
          <div class="stat-card">
            <div class="stat-icon"><el-icon><Document /></el-icon></div>
            <div class="stat-info">
              <div class="stat-value">0</div>
              <div class="stat-label">总变更数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-card">
            <div class="stat-icon"><el-icon><Clock /></el-icon></div>
            <div class="stat-info">
              <div class="stat-value">0</div>
              <div class="stat-label">待审批</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-card">
            <div class="stat-icon"><el-icon><CircleCheck /></el-icon></div>
            <div class="stat-info">
              <div class="stat-value">0</div>
              <div class="stat-label">已发布</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-card">
            <div class="stat-icon"><el-icon><Warning /></el-icon></div>
            <div class="stat-info">
              <div class="stat-value">0</div>
              <div class="stat-label">已回滚</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>最近变更</span>
              <el-link type="primary" @click="$router.push('/changes')">查看全部</el-link>
            </div>
          </template>
          <el-empty description="暂无变更数据" />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>快速操作</template>
          <div class="quick-actions">
            <el-button type="primary" @click="$router.push('/changes/create')">新建变更</el-button>
            <el-button @click="$router.push('/org')">组织架构</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
// 仪表盘页面
</script>

<style scoped>
.dashboard-page {
  padding: 20px;
}
.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
}
.stat-icon {
  font-size: 32px;
  color: #2980b9;
}
.stat-info {
  display: flex;
  flex-direction: column;
}
.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #1a5276;
}
.stat-label {
  font-size: 12px;
  color: #7f8c8d;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
</style>
