<template>
  <div class="gantt-container">
    <!-- 时间轴头部 -->
    <div class="gantt-header">
      <div class="gantt-tasks-header">任务</div>
      <div class="gantt-timeline-header">
        <div
          v-for="day in timelineDays"
          :key="day.key"
          class="timeline-day"
          :class="{ 'is-weekend': day.isWeekend, 'is-today': day.isToday }"
        >
          <div class="day-label">{{ day.dayNum }}</div>
          <div class="weekday-label">{{ day.weekday }}</div>
        </div>
      </div>
    </div>

    <!-- 任务列表 -->
    <div v-loading="loading" class="gantt-body">
      <!-- 任务行 -->
      <div
        v-for="task in displayTasks"
        :key="task.id"
        class="gantt-row"
      >
        <div class="gantt-task-info">
          <div class="task-title" :title="task.content">{{ truncate(task.content, 20) }}</div>
          <div class="task-meta">
            <span
              v-if="task.team_name"
              class="team-badge"
              :style="{ '--team-color': task.team_color || '#909399' }"
            >
              {{ task.team_name }}
            </span>
            <span class="status-badge" :class="`status-${task.status}`">
              {{ statusLabels[task.status] || task.status }}
            </span>
          </div>
        </div>
        <div class="gantt-timeline">
          <!-- 依赖连线 -->
          <svg class="gantt-svg" v-if="hasDependencies">
            <defs>
              <marker
                id="arrowhead"
                markerWidth="10"
                markerHeight="7"
                refX="9"
                refY="3.5"
                orient="auto"
              >
                <polygon
                  points="0 0, 10 3.5, 0 7"
                  :fill="strokeColor"
                />
              </marker>
            </defs>
            <g v-for="dep in dependenciesFromTask(task.id)" :key="dep.id">
              <line
                :x1="getDependencyX1(dep)"
                :y1="getDependencyY1(dep)"
                :x2="getDependencyX2(dep)"
                :y2="getDependencyY2(dep)"
                :stroke="strokeColor"
                stroke-width="2"
                marker-end="url(#arrowhead)"
                class="dependency-line"
              />
            </g>
          </svg>
          <!-- 任务条 -->
          <div
            class="task-bar"
            :class="{ 'is-today-range': isInRange(task) }"
            :style="taskBarStyle(task)"
            @click="handleTaskClick(task)"
          >
            <div class="task-bar-content">
              <span class="task-bar-text">{{ truncate(task.content, 15) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="!loading && displayTasks.length === 0" class="gantt-empty">
        <el-empty description="所选时间段内暂无任务" />
      </div>
    </div>

    <!-- 状态图例 -->
    <div class="gantt-legend">
      <div class="legend-item">
        <span class="legend-dot status-pending"></span>
        待处理
      </div>
      <div class="legend-item">
        <span class="legend-dot status-in-progress"></span>
        进行中
      </div>
      <div class="legend-item">
        <span class="legend-dot status-completed"></span>
        已完成
      </div>
      <div class="legend-item">
        <span class="legend-dot status-cancelled"></span>
        已取消
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { dashboardAPI } from '@/api/dashboard'

const router = useRouter()

interface GanttTask {
  id: string
  content: string
  start_date: string
  end_date: string
  team_id: string | null
  team_name: string | null
  team_color: string | null
  change_type: string
  status: string
}

interface GanttDependency {
  id: string
  from_id: string
  to_id: string
  type: 'FS'
}

interface Props {
  startDate: string
  endDate: string
  teamId?: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'tasks-loaded', count: number): void
}>()

// ── 状态 ──
const loading = ref(false)
const tasks = ref<GanttTask[]>([])
const dependencies = ref<GanttDependency[]>([])

const statusLabels: Record<string, string> = {
  pending: '待处理',
  'in-progress': '进行中',
  completed: '已完成',
  cancelled: '已取消',
}

// ── 计算属性 ──
const timelineDays = computed(() => {
  const days: Array<{
    key: string
    date: Date
    dayNum: number
    weekday: string
    isWeekend: boolean
    isToday: boolean
  }> = []

  const start = new Date(props.startDate)
  const end = new Date(props.endDate)
  const today = new Date()
  const todayKey = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`

  for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
    const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
    days.push({
      key,
      date: new Date(d),
      dayNum: d.getDate(),
      weekday: ['日', '一', '二', '三', '四', '五', '六'][d.getDay()],
      isWeekend: d.getDay() === 0 || d.getDay() === 6,
      isToday: key === todayKey,
    })
  }

  return days
})

const dayWidth = 50 // 每天的像素宽度

const displayTasks = computed(() => {
  // 按开始时间排序
  return [...tasks.value].sort((a, b) => {
    return new Date(a.start_date).getTime() - new Date(b.start_date).getTime()
  })
})

const hasDependencies = computed(() => dependencies.value.length > 0)

const strokeColor = computed(() => {
  return getComputedStyle(document.documentElement).getPropertyValue('--el-text-color-secondary')?.trim() || '#909399'
})

// ── 方法 ──
async function fetchGanttData() {
  loading.value = true
  try {
    const data: any = await dashboardAPI.gantt({
      start_date: props.startDate,
      end_date: props.endDate,
      team_id: props.teamId,
    })
    tasks.value = data.tasks || []
    dependencies.value = data.dependencies || []
    emit('tasks-loaded', tasks.value.length)
  } catch (e) {
    console.error(e)
    ElMessage.error('Gantt 数据加载失败')
  } finally {
    loading.value = false
  }
}

function taskBarStyle(task: GanttTask) {
  const start = new Date(props.startDate)
  const taskStart = new Date(task.start_date)
  const taskEnd = new Date(task.end_date)

  // 计算天数差
  const diffDays = Math.floor((taskEnd.getTime() - taskStart.getTime()) / (1000 * 60 * 60 * 24)) + 1
  const offsetDays = Math.floor((taskStart.getTime() - start.getTime()) / (1000 * 60 * 60 * 24))

  return {
    left: `${offsetDays * dayWidth}px`,
    width: `${diffDays * dayWidth}px`,
    '--team-color': task.team_color || '#909399',
  }
}

function dependenciesFromTask(taskId: string): GanttDependency[] {
  return dependencies.value.filter((dep) => dep.from_id === taskId)
}

function getDependencyX1(dep: GanttDependency): number {
  const fromTask = tasks.value.find((t) => t.id === dep.from_id)
  if (!fromTask) return 0

  const start = new Date(props.startDate)
  const fromEnd = new Date(fromTask.end_date)
  const offsetDays = Math.floor((fromEnd.getTime() - start.getTime()) / (1000 * 60 * 60 * 24)) + 1

  return offsetDays * dayWidth
}

function getDependencyY1(dep: GanttDependency): number {
  const index = displayTasks.value.findIndex((t) => t.id === dep.from_id)
  const rowHeight = 60
  return index * rowHeight + rowHeight / 2
}

function getDependencyX2(dep: GanttDependency): number {
  const toTask = tasks.value.find((t) => t.id === dep.to_id)
  if (!toTask) return 0

  const start = new Date(props.startDate)
  const toStart = new Date(toTask.start_date)
  const offsetDays = Math.floor((toStart.getTime() - start.getTime()) / (1000 * 60 * 60 * 24))

  return offsetDays * dayWidth
}

function getDependencyY2(dep: GanttDependency): number {
  const index = displayTasks.value.findIndex((t) => t.id === dep.to_id)
  const rowHeight = 60
  return index * rowHeight + rowHeight / 2
}

function isInRange(task: GanttTask): boolean {
  const today = new Date()
  const todayKey = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`
  return todayKey >= task.start_date && todayKey <= task.end_date
}

function handleTaskClick(task: GanttTask) {
  router.push(`/changes/${task.id}`)
}

function truncate(s: string, n = 20) {
  if (!s) return ''
  return s.length > n ? s.slice(0, n) + '…' : s
}

// ── 生命周期 ──
watch(() => [props.startDate, props.endDate, props.teamId], fetchGanttData)
onMounted(fetchGanttData)
</script>

<style scoped>
.gantt-container {
  --gantt-bg: var(--el-bg-color, #ffffff);
  --gantt-border: var(--el-border-color-lighter, #e4e7ed);
  --gantt-text: var(--el-text-color-primary, #303133);
  --gantt-text-soft: var(--el-text-color-secondary, #909399);
  --gantt-page-bg: var(--el-bg-color-page, #f5f7fa);
  --day-width: 50px;

  background: var(--gantt-bg);
  border: 1px solid var(--gantt-border);
  border-radius: 10px;
  overflow: hidden;
}

/* 暗色模式 - 实际样式在 <style> 块中（未 scoped） */

/* ── 头部 ── */
.gantt-header {
  display: flex;
  border-bottom: 1px solid var(--gantt-border);
  background: var(--gantt-bg);
  position: sticky;
  top: 0;
  z-index: 10;
}

.gantt-tasks-header {
  width: 220px;
  min-width: 220px;
  padding: 12px 16px;
  font-weight: 600;
  color: var(--gantt-text);
  border-right: 1px solid var(--gantt-border);
  display: flex;
  align-items: center;
}

.gantt-timeline-header {
  flex: 1;
  display: flex;
  overflow-x: auto;
}

.timeline-day {
  width: var(--day-width);
  min-width: var(--day-width);
  padding: 8px 4px;
  text-align: center;
  border-right: 1px solid var(--gantt-border);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.timeline-day.is-weekend {
  background: var(--gantt-page-bg);
}

.timeline-day.is-today {
  background: rgba(26, 82, 118, 0.08);
}

.day-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--gantt-text);
  margin-bottom: 2px;
}

.weekday-label {
  font-size: 11px;
  color: var(--gantt-text-soft);
}

/* ── 主体 ── */
.gantt-body {
  max-height: 600px;
  overflow-y: auto;
  position: relative;
}

.gantt-row {
  display: flex;
  border-bottom: 1px solid var(--gantt-border);
  min-height: 60px;
  position: relative;
}

.gantt-row:last-child {
  border-bottom: none;
}

.gantt-task-info {
  width: 220px;
  min-width: 220px;
  padding: 12px 16px;
  border-right: 1px solid var(--gantt-border);
  display: flex;
  flex-direction: column;
  justify-content: center;
  background: var(--gantt-bg);
  position: sticky;
  left: 0;
  z-index: 5;
}

.task-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--gantt-text);
  margin-bottom: 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.task-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.team-badge {
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 4px;
  background: color-mix(in srgb, var(--team-color) 12%, transparent);
  border-left: 2px solid var(--team-color);
  color: var(--gantt-text);
}

.status-badge {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 500;
}

.status-badge.status-pending {
  background: var(--el-fill-color-light, #f0f2f5);
  color: var(--el-text-color-secondary, #909399);
}

.status-badge.status-in-progress {
  background: #e6f7ff;
  color: #1890ff;
}

.status-badge.status-completed {
  background: #f6ffed;
  color: #52c41a;
}

.status-badge.status-cancelled {
  background: var(--el-fill-color-light, #f0f2f5);
  color: var(--el-text-color-placeholder, #c0c4cc);
  text-decoration: line-through;
}

/* 暗色模式下状态徽章 - 在 <style> 全局块中 */

.gantt-timeline {
  flex: 1;
  position: relative;
  min-height: 60px;
  overflow-x: auto;
}

.gantt-svg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
}

.dependency-line {
  pointer-events: none;
}

.task-bar {
  position: absolute;
  top: 12px;
  height: 36px;
  border-radius: 6px;
  background: color-mix(in srgb, var(--team-color) 20%, transparent);
  border-left: 3px solid var(--team-color);
  border-right: 1px solid var(--team-color);
  cursor: pointer;
  transition: all 0.15s;
  z-index: 2;
  display: flex;
  align-items: center;
  padding: 0 8px;
}

.task-bar:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  background: color-mix(in srgb, var(--team-color) 28%, transparent);
}

.task-bar.is-today-range {
  box-shadow: 0 0 0 2px rgba(26, 82, 118, 0.3);
}

.task-bar-content {
  flex: 1;
  min-width: 0;
}

.task-bar-text {
  font-size: 12px;
  font-weight: 500;
  color: var(--gantt-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* ── 空状态 ── */
.gantt-empty {
  padding: 60px 20px;
  text-align: center;
}

/* ── 图例 ── */
.gantt-legend {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 16px;
  border-top: 1px solid var(--gantt-border);
  background: var(--gantt-bg);
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--gantt-text-soft);
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.legend-dot.status-pending {
  background: var(--el-text-color-secondary, #909399);
}

.legend-dot.status-in-progress {
  background: #1890ff;
}

.legend-dot.status-completed {
  background: #52c41a;
}

.legend-dot.status-cancelled {
  background: var(--el-text-color-placeholder, #c0c4cc);
}

/* ── 响应式 ── */
@media (max-width: 768px) {
  .gantt-tasks-header {
    width: 160px;
    min-width: 160px;
  }

  .gantt-task-info {
    width: 160px;
    min-width: 160px;
  }

  .timeline-day {
    width: 36px;
    min-width: 36px;
  }

  :root {
    --day-width: 36px;
  }
}
</style>

<style>
/* 暗色模式 - 未 scoped 样式以匹配 html.dark / html.gg-dark 父类 */
html.dark .gantt-container,
html.gg-dark .gantt-container,
.dark .gantt-container,
.gg-dark .gantt-container {
  --gantt-border: var(--gg-border, #2a2a3a) !important;
  --gantt-bg: var(--gg-card, #1f232b) !important;
  --gantt-page-bg: var(--gg-bg, #15171c) !important;
  --gantt-text: var(--gg-text, #e0e0e0) !important;
  --gantt-text-soft: var(--gg-text-muted, #888899) !important;
}

html.dark .gantt-container .status-badge.status-in-progress,
html.gg-dark .gantt-container .status-badge.status-in-progress,
.dark .gantt-container .status-badge.status-in-progress,
.gg-dark .gantt-container .status-badge.status-in-progress {
  background: rgba(24, 144, 255, 0.2) !important;
}

html.dark .gantt-container .status-badge.status-completed,
html.gg-dark .gantt-container .status-badge.status-completed,
.dark .gantt-container .status-badge.status-completed,
.gg-dark .gantt-container .status-badge.status-completed {
  background: rgba(82, 196, 26, 0.2) !important;
}
</style>
