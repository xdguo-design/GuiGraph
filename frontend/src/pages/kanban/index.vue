<template>
  <div class="kanban-page">
    <!-- 顶部工具栏 -->
    <div class="kanban-toolbar">
      <div class="toolbar-left">
        <el-button-group>
          <el-button :icon="ArrowLeft" @click="goPrevMonth" />
          <el-button @click="goToday">今天</el-button>
          <el-button :icon="ArrowRight" @click="goNextMonth" />
        </el-button-group>
        <span class="month-label">{{ monthLabel }}</span>
      </div>
      <div class="toolbar-right">
        <!-- 视图切换 -->
        <el-segmented v-model="viewMode" :options="viewOptions">
          <template #default="{ item }">
            <el-icon style="margin-right: 4px">
              <component :is="item.icon" />
            </el-icon>
            {{ item.label }}
          </template>
        </el-segmented>
        <el-select
          v-model="filterTeamId"
          placeholder="所有团队"
          clearable
          style="width: 220px"
          @change="handleTeamChange"
        >
          <el-option
            v-for="t in teams"
            :key="t.id"
            :label="t.name"
            :value="t.id"
          >
            <span class="team-option">
              <span class="dot" :style="{ background: t.color }"></span>
              {{ t.name }}
            </span>
          </el-option>
        </el-select>
      </div>
    </div>

    <!-- 团队色卡图例 -->
    <div v-if="teams.length" class="team-legend">
      <span
        v-for="t in teams"
        :key="t.id"
        class="legend-item"
      >
        <span class="dot" :style="{ background: t.color }"></span>
        {{ t.name }}
      </span>
    </div>

    <!-- 日历视图 -->
    <div v-show="viewMode === 'calendar'" v-loading="loading" class="calendar-wrapper">
      <div class="calendar">
        <!-- 表头：周一~周日 -->
        <div class="cal-header">
          <div v-for="w in weekHeaders" :key="w" class="cal-cell head-cell">{{ w }}</div>
        </div>
        <!-- 每一周一行 -->
        <div
          v-for="(week, wi) in calendarWeeks"
          :key="wi"
          class="cal-row"
        >
          <div
            v-for="(day, di) in week"
            :key="di"
            class="cal-cell day-cell"
            :class="{
              'out-of-month': !day.inMonth,
              'is-today': day.isToday,
              'is-weekend': day.isWeekend,
            }"
            @click="handleDayClick(day)"
          >
            <div class="day-head">
              <span class="day-num">{{ day.day }}</span>
              <span v-if="day.items.length" class="day-count">{{ day.items.length }}</span>
            </div>
            <div class="day-items">
              <div
                v-for="item in day.items.slice(0, 3)"
                :key="item.id"
                class="day-item"
                :style="{
                  '--team-color': item.team_color || '#909399',
                }"
                :title="`[${item.team_name || '未分配'}] ${item.content}`"
                @click.stop="handleItemClick(item)"
              >
                <el-icon class="item-icon">
                  <component :is="iconForType(item.change_type)" />
                </el-icon>
                <span class="item-text">{{ truncate(item.content) }}</span>
              </div>
              <div v-if="day.items.length > 3" class="day-more">+{{ day.items.length - 3 }} more</div>
            </div>
            <!-- 当日新增（悬浮） -->
            <div v-if="day.inMonth" class="day-add" title="当天上报">
              <el-icon><Plus /></el-icon>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Gantt 视图 -->
    <div v-show="viewMode === 'gantt'" class="gantt-wrapper">
      <KanbanGantt
        :start-date="ganttStartDate"
        :end-date="ganttEndDate"
        :team-id="filterTeamId"
        @tasks-loaded="handleTasksLoaded"
      />
    </div>

    <!-- 月度热力看板 -->
    <div class="heatmap-section">
      <div class="heatmap-title">月度热力看板</div>
      <div class="heatmap-grid">
        <div
          v-for="m in heatmapMonths"
          :key="m.key"
          class="heatmap-cell"
          :class="{ 'is-active': m.key === currentMonthKey }"
          :style="heatCellStyle(m.count)"
          :title="`${m.label}: ${m.count} 条`"
          @click="goMonth(m.key)"
        >
          <span class="heat-label">{{ m.label }}</span>
          <span class="heat-count">{{ m.count }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, ArrowRight, Plus, Document, Edit, CircleCheck, Warning, Histogram, Calendar, Grid } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { dashboardAPI } from '@/api/dashboard'
import KanbanGantt from '@/components/business/KanbanGantt.vue'

const router = useRouter()

// ── 视图模式 ──
const viewMode = ref<'calendar' | 'gantt'>('calendar')
const viewOptions = [
  { label: '日历', value: 'calendar', icon: Calendar },
  { label: 'Gantt', value: 'gantt', icon: Grid },
]

// ── 月份导航 ──
const today = new Date()
const currentMonth = ref(new Date(today.getFullYear(), today.getMonth(), 1))
const currentMonthKey = computed(() => formatMonth(currentMonth.value))
const monthLabel = computed(() => {
  const y = currentMonth.value.getFullYear()
  const m = currentMonth.value.getMonth() + 1
  return `${y} 年 ${m} 月`
})

// Gantt 视图日期范围（显示当前月的前后各两周）
const ganttStartDate = computed(() => {
  const d = new Date(currentMonth.value)
  d.setDate(d.getDate() - 14)
  return formatDate(d)
})

const ganttEndDate = computed(() => {
  const d = new Date(currentMonth.value)
  d.setMonth(d.getMonth() + 1)
  d.setDate(d.getDate() + 13)
  return formatDate(d)
})

function formatMonth(d: Date) {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
}

function formatDate(d: Date) {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

function shiftMonth(delta: number) {
  const d = new Date(currentMonth.value)
  d.setMonth(d.getMonth() + delta)
  currentMonth.value = d
}
function goPrevMonth() { shiftMonth(-1) }
function goNextMonth() { shiftMonth(1) }
function goToday() {
  currentMonth.value = new Date(today.getFullYear(), today.getMonth(), 1)
}
function goMonth(key: string) {
  const [y, m] = key.split('-').map(Number)
  currentMonth.value = new Date(y, m - 1, 1)
}

// ── 数据 ──
const loading = ref(false)
const teams = ref<Array<{ id: string; name: string; code: string; color: string }>>([])
const itemsByDay = ref<Record<string, any[]>>({})
const heatmap = ref<Array<{ month: string; count: number }>>([])
const filterTeamId = ref<string>('')

async function fetchKanban() {
  loading.value = true
  try {
    const data: any = await dashboardAPI.kanban({
      month: currentMonthKey.value,
      team_id: filterTeamId.value,
    })
    teams.value = data.teams || []
    itemsByDay.value = data.items_by_day || {}
    heatmap.value = data.heatmap || []
  } catch (e) {
    console.error(e)
    ElMessage.error('看板数据加载失败')
  } finally {
    loading.value = false
  }
}

function handleTeamChange() {
  // 刷新当前视图数据
  if (viewMode.value === 'calendar') {
    fetchKanban()
  }
  // Gantt 视图通过 props 自动更新
}

function handleTasksLoaded(count: number) {
  // Gantt 数据加载完成回调
  console.log(`Gantt 视图加载了 ${count} 个任务`)
}

watch(currentMonth, fetchKanban)
onMounted(fetchKanban)

// ── 日历网格生成 ──
const weekHeaders = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

interface DayCell {
  date: Date
  day: number
  inMonth: boolean
  isToday: boolean
  isWeekend: boolean
  items: any[]
}

const calendarWeeks = computed<DayCell[][]>(() => {
  const y = currentMonth.value.getFullYear()
  const m = currentMonth.value.getMonth()
  const firstOfMonth = new Date(y, m, 1)
  // 周一为一周开始：getDay() 0=Sun, 1=Mon..6=Sat → 转成 0=Mon
  const offset = (firstOfMonth.getDay() + 6) % 7
  const start = new Date(y, m, 1 - offset)
  const weeks: DayCell[][] = []
  const todayKey = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`

  for (let w = 0; w < 6; w++) {
    const row: DayCell[] = []
    for (let d = 0; d < 7; d++) {
      const date = new Date(start)
      date.setDate(start.getDate() + w * 7 + d)
      const key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
      row.push({
        date,
        day: date.getDate(),
        inMonth: date.getMonth() === m,
        isToday: key === todayKey,
        isWeekend: date.getDay() === 0 || date.getDay() === 6,
        items: itemsByDay.value[key] || [],
      })
    }
    weeks.push(row)
  }
  return weeks
})

// ── 热力图（最近 12 个月） ──
const heatmapMonths = computed(() => {
  const months: Array<{ key: string; label: string; count: number }> = []
  const base = new Date(currentMonth.value)
  for (let i = 11; i >= 0; i--) {
    const d = new Date(base.getFullYear(), base.getMonth() - i, 1)
    const key = formatMonth(d)
    const row = heatmap.value.find((h) => h.month === key)
    months.push({
      key,
      label: `${d.getMonth() + 1}月`,
      count: row?.count || 0,
    })
  }
  return months
})

const heatMaxCount = computed(() => Math.max(1, ...heatmapMonths.value.map((m) => m.count)))

function heatCellStyle(count: number) {
  const ratio = count / heatMaxCount.value
  if (count === 0) return { background: 'var(--heat-empty)', color: 'var(--heat-text-soft)' }
  // 越深越亮
  const alpha = 0.25 + ratio * 0.75
  return {
    background: `rgba(26, 82, 118, ${alpha.toFixed(2)})`,
    color: ratio > 0.4 ? '#fff' : 'var(--heat-text)',
  }
}

// ── 交互 ──
function handleDayClick(day: DayCell) {
  if (day.items.length === 0) {
    // 空格子 → 当天上报
    const y = day.date.getFullYear()
    const m = String(day.date.getMonth() + 1).padStart(2, '0')
    const d = String(day.date.getDate()).padStart(2, '0')
    router.push({ path: '/changes/create', query: { date: `${y}-${m}-${d}` } })
  } else {
    // 有内容 → 不跳转，让用户选择具体条目
  }
}

function handleItemClick(item: any) {
  router.push(`/changes/${item.id}`)
}

function truncate(s: string, n = 14) {
  if (!s) return ''
  return s.length > n ? s.slice(0, n) + '…' : s
}

function iconForType(t: string) {
  switch ((t || '').toLowerCase()) {
    case 'db':
      return Histogram
    case 'update':
      return Edit
    case 'add':
      return Plus
    case 'create':
      return Plus
    case 'delete':
      return Warning
    case 'fix':
      return CircleCheck
    default:
      return Document
  }
}
</script>

<style scoped>
.kanban-page {
  --kanban-radius: 10px;
  --kanban-divider: var(--el-border-color-lighter, #e4e7ed);
  --kanban-cell-bg: var(--el-bg-color, #ffffff);
  --kanban-page-bg: var(--el-bg-color-page, #f5f7fa);
  --kanban-text: var(--el-text-color-primary, #303133);
  --kanban-text-soft: var(--el-text-color-secondary, #909399);
  --heat-empty: var(--el-fill-color-light, #f0f2f5);
  --heat-text: var(--el-text-color-primary, #303133);
  --heat-text-soft: var(--el-text-color-secondary, #909399);
  padding: 4px 2px;
}
/* 暗色模式（html.dark 是 element-plus 推荐做法） */
.kanban-page {
  --kanban-divider: var(--el-border-color-lighter, #e4e7ed);
  --kanban-cell-bg: var(--el-bg-color, #ffffff);
  --kanban-page-bg: var(--el-bg-color-page, #f5f7fa);
  --kanban-text: var(--el-text-color-primary, #303133);
  --kanban-text-soft: var(--el-text-color-secondary, #909399);
  --heat-empty: var(--el-fill-color-light, #f0f2f5);
  --heat-text: var(--el-text-color-primary, #303133);
  --heat-text-soft: var(--el-text-color-secondary, #909399);
}

/* ── 工具栏 ── */
.kanban-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}
.toolbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}
.month-label {
  font-size: 20px;
  font-weight: 600;
  color: var(--kanban-text);
}
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.team-option {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

/* ── 团队色卡图例 ── */
.team-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 14px;
  padding: 10px 14px;
  background: var(--kanban-cell-bg);
  border: 1px solid var(--kanban-divider);
  border-radius: var(--kanban-radius);
}
.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--kanban-text);
}
.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}

/* ── 月历 ── */
.calendar-wrapper {
  background: var(--kanban-cell-bg);
  border: 1px solid var(--kanban-divider);
  border-radius: var(--kanban-radius);
  overflow: hidden;
  margin-bottom: 20px;
}
.calendar {
  display: flex;
  flex-direction: column;
}
.cal-header {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  background: var(--kanban-cell-bg);
  border-bottom: 1px solid var(--kanban-divider);
}
.head-cell {
  padding: 10px 12px;
  font-size: 13px;
  font-weight: 600;
  color: var(--kanban-text-soft);
  text-align: center;
  border-right: 1px solid var(--kanban-divider);
}
.head-cell:last-child {
  border-right: none;
}
.cal-row {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  min-height: 110px;
  border-bottom: 1px solid var(--kanban-divider);
}
.cal-row:last-child {
  border-bottom: none;
}
.day-cell {
  position: relative;
  padding: 8px 10px;
  border-right: 1px solid var(--kanban-divider);
  cursor: pointer;
  transition: background 0.15s;
  display: flex;
  flex-direction: column;
  background: var(--kanban-cell-bg);
}
.day-cell:last-child {
  border-right: none;
}
.day-cell:hover {
  background: var(--kanban-page-bg);
}
.day-cell.out-of-month {
  opacity: 0.45;
}
.day-cell.is-today {
  background: rgba(26, 82, 118, 0.06);
}
.day-cell.is-today .day-num {
  color: #fff;
  background: linear-gradient(135deg, #1a5276 0%, #2980b9 100%);
}
.day-cell.is-weekend {
  background: var(--kanban-page-bg);
}
.day-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}
.day-num {
  font-size: 13px;
  font-weight: 600;
  color: var(--kanban-text);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 24px;
  height: 24px;
  padding: 0 6px;
  border-radius: 12px;
}
.day-count {
  font-size: 11px;
  color: var(--kanban-text-soft);
  background: var(--kanban-page-bg);
  padding: 1px 6px;
  border-radius: 8px;
}
.day-items {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 3px;
  overflow: hidden;
}
.day-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  line-height: 1.4;
  padding: 2px 6px;
  border-radius: 4px;
  background: color-mix(in srgb, var(--team-color) 14%, transparent);
  border-left: 2px solid var(--team-color);
  color: var(--kanban-text);
  cursor: pointer;
  transition: background 0.15s;
  max-width: 100%;
  overflow: hidden;
}
.day-item:hover {
  background: color-mix(in srgb, var(--team-color) 24%, transparent);
}
.item-icon {
  font-size: 11px;
  color: var(--team-color);
  flex-shrink: 0;
}
.item-text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
  min-width: 0;
  font-weight: 500;
}
.day-more {
  font-size: 11px;
  color: var(--kanban-text-soft);
  padding: 0 6px;
}
.day-add {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: var(--kanban-page-bg);
  color: var(--kanban-text-soft);
  font-size: 12px;
  opacity: 0;
  transition: opacity 0.15s;
}
.day-cell:hover .day-add {
  opacity: 1;
}

/* ── Gantt 包装 ── */
.gantt-wrapper {
  margin-bottom: 20px;
}

/* ── 热力图 ── */
.heatmap-section {
  background: var(--kanban-cell-bg);
  border: 1px solid var(--kanban-divider);
  border-radius: var(--kanban-radius);
  padding: 14px 16px;
}
.heatmap-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--kanban-text);
  margin-bottom: 10px;
}
.heatmap-grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 6px;
}
.heatmap-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 10px 4px;
  border-radius: 6px;
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.15s;
}
.heatmap-cell:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}
.heatmap-cell.is-active {
  outline: 2px solid #1a5276;
  outline-offset: 1px;
}
.heat-label {
  font-size: 12px;
  font-weight: 500;
  margin-bottom: 2px;
}
.heat-count {
  font-size: 16px;
  font-weight: 600;
}

/* 响应式 */
@media (max-width: 1100px) {
  .heatmap-grid {
    grid-template-columns: repeat(6, 1fr);
  }
}
@media (max-width: 700px) {
  .heatmap-grid {
    grid-template-columns: repeat(4, 1fr);
  }
  .cal-row {
    min-height: 80px;
  }
}
</style>

<style>
/* 暗色模式 - 未 scoped 样式以确保正确的优先级 */
html.dark .kanban-page,
html.gg-dark .kanban-page,
.dark .kanban-page,
.gg-dark .kanban-page {
  --kanban-divider: var(--gg-border, #2a2a3a) !important;
  --kanban-cell-bg: var(--gg-card, #1f232b) !important;
  --kanban-page-bg: var(--gg-bg, #15171c) !important;
  --kanban-text: var(--gg-text, #e0e0e0) !important;
  --kanban-text-soft: var(--gg-text-muted, #888899) !important;
  --heat-empty: var(--gg-border, #2a2a3a) !important;
  --heat-text: var(--gg-text, #e0e0e0) !important;
  --heat-text-soft: var(--gg-text-muted, #888899) !important;
}
</style>
