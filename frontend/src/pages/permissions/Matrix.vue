<template>
  <div class="permissions-matrix-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>🔐 权限矩阵</span>
          <el-button @click="exportCSV" :icon="Download">导出 CSV</el-button>
        </div>
      </template>

      <!-- 筛选栏 -->
      <div class="filter-bar">
        <el-form :inline="true" :model="filters" class="filter-form">
          <el-form-item label="角色筛选">
            <el-select v-model="filters.role" placeholder="全部角色" clearable style="width: 160px" @change="handleFilterChange">
              <el-option v-for="role in roles" :key="role.key" :label="role.label" :value="role.key" />
            </el-select>
          </el-form-item>
          <el-form-item label="资源筛选">
            <el-select v-model="filters.resource" placeholder="全部资源" clearable style="width: 160px" @change="handleFilterChange">
              <el-option v-for="res in resources" :key="res" :label="res" :value="res" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 权限矩阵表格 -->
      <div class="matrix-wrapper">
        <el-table
          :data="filteredMatrix"
          stripe
          border
          class="matrix-table"
          :row-class-name="getRowClassName"
        >
          <el-table-column prop="roleLabel" label="角色" fixed="left" width="140">
            <template #default="{ row }">
              <div class="role-cell">
                <el-icon class="role-icon"><User /></el-icon>
                <span>{{ row.roleLabel }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column
            v-for="resource in filteredResources"
            :key="resource"
            :label="resource"
            min-width="120"
            align="center"
          >
            <template #default="{ row }">
              <div
                class="permission-cell"
                :class="getCellClass(row.roleKey, resource)"
                @click="handleCellClick(row.roleKey, resource)"
                @mouseenter="showTooltip(row.roleKey, resource)"
                @mouseleave="hideTooltip"
              >
                <span class="permission-count">{{ getPermissionCount(row.roleKey, resource) }}</span>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 图例 -->
      <div class="legend-bar">
        <span class="legend-title">图例：</span>
        <div class="legend-item full">
          <span class="legend-box"></span>
          <span>全权限</span>
        </div>
        <div class="legend-item partial">
          <span class="legend-box"></span>
          <span>部分权限</span>
        </div>
        <div class="legend-item none">
          <span class="legend-box"></span>
          <span>无权限</span>
        </div>
      </div>

      <!-- 统计信息 -->
      <div class="stats-bar">
        <span>📊 权限统计：共 {{ roles.length }} 角色 × {{ filteredResources.length }} 资源 = {{ totalCombinations }} 个权限组合</span>
        <span style="margin-left: 20px;">全权限 {{ stats.full }} 个 | 部分权限 {{ stats.partial }} 个 | 无权限 {{ stats.none }} 个</span>
      </div>
    </el-card>

    <!-- Tooltip 弹窗 -->
    <el-popover
      ref="tooltipRef"
      :visible="tooltipVisible"
      placement="right"
      :width="280"
      trigger="manual"
    >
      <div v-if="tooltipContent" class="permission-tooltip">
        <div class="tooltip-header">
          <strong>{{ tooltipContent.roleLabel }} / {{ tooltipContent.resource }}</strong>
        </div>
        <div class="tooltip-body">
          <el-tag
            v-for="op in tooltipContent.operations"
            :key="op"
            size="small"
            style="margin: 4px;"
          >
            {{ op }}
          </el-tag>
          <el-empty v-if="!tooltipContent.operations?.length" description="无权限" :image-size="60" />
        </div>
      </div>
    </el-popover>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Download, User } from '@element-plus/icons-vue'
import { PERMISSION_MATRIX, ROLE_LABELS, ALL_RESOURCES } from '@/composables/usePermission'

// ── 角色和资源列表 ──
const roles = ref<Array<{ key: string; label: string }>>(
  Object.entries(ROLE_LABELS).map(([key, label]) => ({ key, label }))
)
const resources = ref<string[]>(ALL_RESOURCES)

// ── 筛选器 ──
const filters = reactive({
  role: '',
  resource: '',
})

// ── 计算属性：过滤后的矩阵 ──
const filteredResources = computed(() => {
  if (filters.resource) {
    return resources.value.filter(r => r === filters.resource)
  }
  return resources.value
})

const filteredMatrix = computed(() => {
  let rows = roles.value.map(role => ({
    roleKey: role.key,
    roleLabel: role.label,
  }))

  if (filters.role) {
    rows = rows.filter(r => r.roleKey === filters.role)
  }

  return rows
})

// ── 统计信息 ──
const totalCombinations = computed(() => {
  return roles.value.length * filteredResources.value.length
})

const stats = computed(() => {
  let full = 0
  let partial = 0
  let none = 0

  roles.value.forEach(role => {
    filteredResources.value.forEach(resource => {
      const count = getPermissionCount(role.key, resource)
      const maxCount = getMaxOperationsForResource(resource)
      if (count === 0) none++
      else if (count >= maxCount) full++
      else partial++
    })
  })

  return { full, partial, none }
})

// ── 辅助函数 ──
function getPermissionCount(roleKey: string, resource: string): number {
  return PERMISSION_MATRIX[roleKey]?.[resource]?.length || 0
}

function getMaxOperationsForResource(resource: string): number {
  // 找出拥有该资源最多权限的角色，返回其权限数
  let max = 0
  roles.value.forEach(role => {
    const count = getPermissionCount(role.key, resource)
    if (count > max) max = count
  })
  return max
}

function getCellClass(roleKey: string, resource: string): string {
  const count = getPermissionCount(roleKey, resource)
  if (count === 0) return 'permission-none'
  if (count >= getMaxOperationsForResource(resource)) return 'permission-full'
  return 'permission-partial'
}

function getRowClassName({ row }: { row: { roleKey: string } }): string {
  return `role-row-${row.roleKey}`
}

// ── 交互处理 ──
function handleFilterChange() {
  // 筛选变化时自动更新
}

function handleReset() {
  filters.role = ''
  filters.resource = ''
  ElMessage.success('已重置筛选')
}

function handleCellClick(roleKey: string, resource: string) {
  // 点击单元格时的处理（可选：高亮行/列）
  console.log('Clicked:', roleKey, resource)
}

// ── Tooltip ──
const tooltipVisible = ref(false)
const tooltipContent = ref<{
  roleLabel: string
  resource: string
  operations: string[]
} | null>(null)

function showTooltip(roleKey: string, resource: string) {
  const operations = PERMISSION_MATRIX[roleKey]?.[resource] || []
  tooltipContent.value = {
    roleLabel: ROLE_LABELS[roleKey],
    resource,
    operations,
  }
  tooltipVisible.value = true
}

function hideTooltip() {
  tooltipVisible.value = false
}

// ── 导出 CSV ──
function exportCSV() {
  const headers = ['角色', ...filteredResources.value]
  const rows = filteredMatrix.value.map(row => {
    const rolePerms = [row.roleLabel]
    filteredResources.value.forEach(resource => {
      const ops = PERMISSION_MATRIX[row.roleKey]?.[resource] || []
      rolePerms.push(ops.length > 0 ? ops.join(', ') : '无权限')
    })
    return rolePerms
  })

  const csvContent = [
    headers.join(','),
    ...rows.map(row => row.join(',')),
  ].join('\n')

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `permissions-matrix-${new Date().toISOString().split('T')[0]}.csv`
  link.click()
  ElMessage.success('导出成功')
}

onMounted(() => {
  console.log('权限矩阵已加载')
})
</script>

<style scoped>
.permissions-matrix-page {
  padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.filter-bar {
  margin-bottom: 20px;
}
.filter-form {
  margin-bottom: 0;
}
.matrix-wrapper {
  margin: 20px 0;
  overflow-x: auto;
}
.matrix-table {
  width: 100%;
}

.role-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}
.role-icon {
  color: #1a5276;
}

.permission-cell {
  position: relative;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  min-height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.permission-cell:hover {
  transform: scale(1.05);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
.permission-count {
  font-weight: 600;
  font-size: 14px;
}

.permission-full {
  background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
  color: #fff;
}
.permission-partial {
  background: linear-gradient(135deg, #f39c12 0%, #f1c40f 100%);
  color: #fff;
}
.permission-none {
  background: #e0e0e0;
  color: #999;
}

.legend-bar {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 16px 0;
  border-top: 1px solid var(--el-border-color-lighter);
}
.legend-title {
  font-weight: 600;
  color: var(--el-text-color-primary);
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
}
.legend-box {
  width: 24px;
  height: 24px;
  border-radius: 4px;
}
.legend-item.full .legend-box {
  background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
}
.legend-item.partial .legend-box {
  background: linear-gradient(135deg, #f39c12 0%, #f1c40f 100%);
}
.legend-item.none .legend-box {
  background: #e0e0e0;
}

.stats-bar {
  padding: 12px 16px;
  background: var(--el-fill-color-light);
  border-radius: 6px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
  display: flex;
  align-items: center;
  flex-wrap: wrap;
}

.permission-tooltip {
  padding: 12px;
}
.tooltip-header {
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}
.tooltip-body {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

/* 暗色模式适配 */
:deep(html.dark) .permission-none {
  background: #2a2f3a;
  color: #6b7280;
}
:deep(html.dark) .stats-bar {
  background: var(--el-fill-color);
}
</style>
