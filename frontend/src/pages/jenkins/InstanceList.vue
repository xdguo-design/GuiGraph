<template>
  <div class="jenkins-list-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>Jenkins 实例</span>
          <el-button type="primary" @click="handleAdd">添加实例</el-button>
        </div>
      </template>
      <el-table :data="instances" v-loading="loading">
        <el-table-column prop="name" label="实例名称" />
        <el-table-column prop="url" label="URL" min-width="300" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'online' ? 'success' : 'danger'">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewBuilds(row.id)">构建历史</el-button>
            <el-button link type="primary" @click="handleEdit(row.id)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const loading = ref(false)
const instances = ref([])

function handleAdd() {
  // TODO: 打开添加对话框
}

function viewBuilds(instanceId: string) {
  // TODO: 查看构建历史
}

function handleEdit(instanceId: string) {
  // TODO: 编辑实例
}
</script>

<style scoped>
.jenkins-list-page {
  padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
