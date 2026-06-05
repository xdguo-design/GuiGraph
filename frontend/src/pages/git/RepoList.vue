<template>
  <div class="repo-list-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>Git 仓库</span>
          <el-button type="primary" @click="handleAdd">添加仓库</el-button>
        </div>
      </template>
      <el-table :data="repos" v-loading="loading">
        <el-table-column prop="name" label="仓库名称" />
        <el-table-column prop="url" label="仓库地址" min-width="300" show-overflow-tooltip />
        <el-table-column prop="default_branch" label="默认分支" width="120" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewBranches(row.id)">分支</el-button>
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
const repos = ref([])

function handleAdd() {
  // TODO: 打开添加对话框
}

function viewBranches(repoId: string) {
  // TODO: 查看分支
}

function handleEdit(repoId: string) {
  // TODO: 编辑仓库
}
</script>

<style scoped>
.repo-list-page {
  padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
