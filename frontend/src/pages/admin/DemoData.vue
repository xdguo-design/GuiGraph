<template>
  <div class="demo-data-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>演示数据管理</span>
          <el-tag type="warning" size="small">仅供测试使用</el-tag>
        </div>
      </template>

      <p class="hint">
        一键灌入演示数据：8 个虚拟用户（覆盖 6 种角色）、完整的组织架构、人员-团队绑定、12 条变更记录、6 条升级日志。
        可用于演示个人/团队看板、组织结构维护、人员权限维护等场景。
      </p>

      <el-row :gutter="16">
        <el-col :span="12">
          <el-button type="primary" size="large" :loading="seeding" @click="handleSeed" style="width: 100%">
            <el-icon><Plus /></el-icon> 灌入演示数据
          </el-button>
        </el-col>
        <el-col :span="12">
          <el-button type="danger" size="large" :loading="clearing" @click="handleClear" style="width: 100%">
            <el-icon><Delete /></el-icon> 清空演示数据
          </el-button>
        </el-col>
      </el-row>

      <el-divider v-if="virtualUsers.length" />

      <template v-if="virtualUsers.length">
        <h3>虚拟账号（密码见 username 一致）</h3>
        <el-table :data="virtualUsers" stripe>
          <el-table-column prop="username" label="用户名" width="120" />
          <el-table-column prop="password" label="密码" width="140" />
          <el-table-column prop="role" label="角色" width="140" />
          <el-table-column prop="team" label="所属团队">
            <template #default="{ row }">{{ row.team || '—' }}</template>
          </el-table-column>
          <el-table-column label="操作" width="100">
            <template #default="{ row }">
              <el-button size="small" link type="primary" @click="copy(row)">复制账号</el-button>
            </template>
          </el-table-column>
        </el-table>
        <p class="tip">说明：所有账号的密码等于 username 后追加 "123"，例如 alice / alice123</p>
      </template>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'
import { demoAPI } from '@/api/application'
import { msgSuccess, msgError, confirmDanger, copyToClipboard } from '@/utils/pageTools'

const seeding = ref(false)
const clearing = ref(false)
const virtualUsers = ref<any[]>([])

async function handleSeed() {
  seeding.value = true
  try {
    const res: any = await demoAPI.seed()
    virtualUsers.value = res?.virtual_users || []
    msgSuccess(`演示数据灌入完成：${JSON.stringify(res?.created || {})}`)
  } catch (e) {
    console.error(e)
  } finally {
    seeding.value = false
  }
}

async function handleClear() {
  const ok = await confirmDanger('将删除所有演示数据（虚拟用户、组织、变更、升级日志），admin 账号保留。是否继续？', '清空演示数据')
  if (!ok) return
  clearing.value = true
  try {
    const res: any = await demoAPI.clear()
    virtualUsers.value = []
    msgSuccess(`演示数据已清空：${JSON.stringify(res?.removed || {})}`)
  } catch (e) {
    console.error(e)
  } finally {
    clearing.value = false
  }
}

async function copy(row: any) {
  await copyToClipboard(`${row.username} / ${row.password}`)
}
</script>

<style scoped>
.demo-data-page {
  padding: 0;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.hint {
  color: #5a6e7a;
  background: #ecf5ff;
  border-left: 3px solid #409eff;
  padding: 12px;
  border-radius: 4px;
  margin: 0 0 16px;
}
.tip {
  color: #909399;
  font-size: 12px;
  margin: 8px 0 0;
}
h3 {
  margin: 0 0 12px;
  color: #303133;
}
</style>
