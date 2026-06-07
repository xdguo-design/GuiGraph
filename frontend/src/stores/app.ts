import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export type ThemeName = 'business' | 'tech' | 'minimal'

const STORAGE_KEY = 'guigraph_theme'

const THEME_PRESETS: Record<ThemeName, Record<string, string>> = {
  // 商务蓝（默认，与登录页同款渐变）
  business: {
    '--gg-primary': '#1a5276',
    '--gg-primary-light': '#2980b9',
    '--gg-primary-dark': '#154360',
    '--gg-bg': '#f8f9fa',
    '--gg-card': '#ffffff',
    '--gg-text': '#2c3e50',
    '--gg-text-muted': '#7f8c8d',
    '--gg-border': '#d5dbdb',
    '--gg-code': '#f4f6f7',
    '--gg-accent': '#e74c3c',
    '--gg-success': '#27ae60',
    '--gg-warning': '#f39c12',
    '--gg-info': '#3498db',
  },
  // 科技黑
  tech: {
    '--gg-primary': '#00d4ff',
    '--gg-primary-light': '#00b8e6',
    '--gg-primary-dark': '#0099cc',
    '--gg-bg': '#0a0a0f',
    '--gg-card': '#12121a',
    '--gg-text': '#e0e0e0',
    '--gg-text-muted': '#888899',
    '--gg-border': '#2a2a3a',
    '--gg-code': '#1a1a2a',
    '--gg-accent': '#ff4757',
    '--gg-success': '#00ff88',
    '--gg-warning': '#ffa502',
    '--gg-info': '#00d4ff',
  },
  // 极简白
  minimal: {
    '--gg-primary': '#2d3436',
    '--gg-primary-light': '#636e72',
    '--gg-primary-dark': '#1a1a1a',
    '--gg-bg': '#ffffff',
    '--gg-card': '#ffffff',
    '--gg-text': '#2d3436',
    '--gg-text-muted': '#b2bec3',
    '--gg-border': '#dfe6e9',
    '--gg-code': '#fafafa',
    '--gg-accent': '#d63031',
    '--gg-success': '#00b894',
    '--gg-warning': '#fdcb6e',
    '--gg-info': '#0984e3',
  },
}

function applyTheme(name: ThemeName) {
  const preset = THEME_PRESETS[name]
  if (!preset) return
  const root = document.documentElement
  for (const [k, v] of Object.entries(preset)) {
    root.style.setProperty(k, v)
  }
  // tech 主题：把 body 设为深色，便于 element-plus 自动适配
  if (name === 'tech') {
    document.documentElement.classList.add('gg-dark')
  } else {
    document.documentElement.classList.remove('gg-dark')
  }
  root.setAttribute('data-gg-theme', name)
}

function readStoredTheme(): ThemeName {
  const t = localStorage.getItem(STORAGE_KEY)
  if (t === 'business' || t === 'tech' || t === 'minimal') return t
  return 'business'
}

export const useAppStore = defineStore('app', () => {
  const sidebarCollapsed = ref(false)
  const theme = ref<ThemeName>(readStoredTheme())

  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  function setTheme(name: ThemeName) {
    theme.value = name
  }

  // 启动时立即应用一次，watch 后续变更同步到 DOM
  applyTheme(theme.value)
  watch(theme, (n) => {
    applyTheme(n)
    localStorage.setItem(STORAGE_KEY, n)
  })

  return { sidebarCollapsed, theme, toggleSidebar, setTheme }
})
