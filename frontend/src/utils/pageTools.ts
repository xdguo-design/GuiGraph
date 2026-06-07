/**
 * 统一页面工具集
 * 封装常用的页面操作：消息提示、确认弹窗、导航等
 */
import { ElMessage, ElMessageBox, ElNotification, MessageBoxData } from 'element-plus'
import type { MessageOptions, MessageBoxOptions } from 'element-plus'

/* ========== 消息提示 ========== */

/** 成功提示 */
export function msgSuccess(message: string, options?: Partial<MessageOptions>) {
  return ElMessage.success({ message, duration: 2000, ...options })
}

/** 错误提示 */
export function msgError(message: string, options?: Partial<MessageOptions>) {
  return ElMessage.error({ message, duration: 3000, ...options })
}

/** 警告提示 */
export function msgWarning(message: string, options?: Partial<MessageOptions>) {
  return ElMessage.warning({ message, duration: 2500, ...options })
}

/** 信息提示 */
export function msgInfo(message: string, options?: Partial<MessageOptions>) {
  return ElMessage.info({ message, duration: 2000, ...options })
}

/* ========== 通知 ========== */

/** 成功通知 */
export function notifySuccess(title: string, message: string) {
  return ElNotification.success({ title, message, duration: 4500 })
}

/** 错误通知 */
export function notifyError(title: string, message: string) {
  return ElNotification.error({ title, message, duration: 0 }) // 不自动关闭
}

/** 警告通知 */
export function notifyWarning(title: string, message: string) {
  return ElNotification.warning({ title, message, duration: 4500 })
}

/* ========== 确认弹窗 ========== */

export interface ConfirmOptions {
  title?: string
  message: string
  confirmText?: string
  cancelText?: string
  type?: 'warning' | 'info' | 'success' | 'error'
  dangerously?: boolean // 危险操作：使用 error 类型样式
}

/**
 * 通用确认弹窗
 * @returns true 确认；false/catch 取消
 */
export async function confirm(options: ConfirmOptions): Promise<boolean> {
  const {
    title = '确认',
    message,
    confirmText = '确定',
    cancelText = '取消',
    type = 'warning',
    dangerously = false,
  } = options
  try {
    const boxOptions: MessageBoxOptions = {
      title,
      message,
      confirmButtonText: confirmText,
      cancelButtonText: cancelText,
      type: dangerously ? 'error' : type,
      draggable: true,
      closeOnClickModal: false,
    }
    await ElMessageBox.confirm(message, title, boxOptions)
    return true
  } catch {
    return false
  }
}

/**
 * 危险操作确认（删除等不可恢复操作）
 */
export async function confirmDanger(message: string, title = '危险操作'): Promise<boolean> {
  return confirm({
    title,
    message,
    type: 'error',
    dangerously: true,
    confirmText: '确认删除',
  })
}

/**
 * 弹窗输入框
 * @param title 弹窗标题
 * @param placeholder 输入框占位符
 * @returns 用户输入的内容，失败返回 null
 */
export async function prompt(
  title: string,
  placeholder = '请输入',
  options?: Partial<MessageBoxOptions>
): Promise<string | null> {
  try {
    const result: MessageBoxData = await ElMessageBox.prompt(placeholder, title, {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPlaceholder: placeholder,
      ...options,
    })
    return result.value || null
  } catch {
    return null
  }
}

/* ========== 导航工具 ========== */

import { useRouter } from 'vue-router'

/**
 * 编程式导航封装
 */
export function usePageNav() {
  const router = useRouter()
  return {
    /** 跳转到指定路径 */
    to: (path: string, query?: Record<string, any>) => {
      router.push({ path, query })
    },
    /** 替换当前路由 */
    replace: (path: string) => {
      router.replace(path)
    },
    /** 后退 */
    back: () => {
      router.back()
    },
    /** 前进 */
    forward: () => {
      router.forward()
    },
    /** 跳转到登录页 */
    toLogin: (redirect?: string) => {
      router.push({ path: '/login', query: redirect ? { redirect } : undefined })
    },
    /** 跳转到 404 */
    toNotFound: () => {
      router.push('/404')
    },
  }
}

/* ========== 本地存储工具 ========== */

export const storage = {
  get<T = any>(key: string, defaultValue?: T): T | null {
    try {
      const val = localStorage.getItem(key)
      if (val === null) return defaultValue ?? null
      try {
        return JSON.parse(val) as T
      } catch {
        return val as unknown as T
      }
    } catch {
      return defaultValue ?? null
    }
  },
  set(key: string, value: any) {
    try {
      localStorage.setItem(key, typeof value === 'string' ? value : JSON.stringify(value))
    } catch (e) {
      console.error('storage.set error:', e)
    }
  },
  remove(key: string) {
    localStorage.removeItem(key)
  },
  clear() {
    localStorage.clear()
  },
}

/* ========== 格式化工具 ========== */

/** 格式化日期时间 */
export function formatDateTime(date: string | Date | null | undefined, fmt = 'YYYY-MM-DD HH:mm:ss'): string {
  if (!date) return '-'
  const d = typeof date === 'string' ? new Date(date) : date
  if (isNaN(d.getTime())) return '-'
  const pad = (n: number) => String(n).padStart(2, '0')
  return fmt
    .replace('YYYY', String(d.getFullYear()))
    .replace('MM', pad(d.getMonth() + 1))
    .replace('DD', pad(d.getDate()))
    .replace('HH', pad(d.getHours()))
    .replace('mm', pad(d.getMinutes()))
    .replace('ss', pad(d.getSeconds()))
}

/** 文件大小格式化 */
export function formatFileSize(bytes: number): string {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let i = 0
  let size = bytes
  while (size >= 1024 && i < units.length - 1) {
    size /= 1024
    i++
  }
  return `${size.toFixed(2)} ${units[i]}`
}

/* ========== 防抖节流 ========== */

/** 防抖 */
export function debounce<T extends (...args: any[]) => any>(fn: T, delay = 300) {
  let timer: ReturnType<typeof setTimeout> | null = null
  return function (this: any, ...args: Parameters<T>) {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => fn.apply(this, args), delay)
  }
}

/** 节流 */
export function throttle<T extends (...args: any[]) => any>(fn: T, delay = 300) {
  let last = 0
  return function (this: any, ...args: Parameters<T>) {
    const now = Date.now()
    if (now - last >= delay) {
      last = now
      fn.apply(this, args)
    }
  }
}

/* ========== 复制到剪贴板 ========== */

export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    if (navigator.clipboard) {
      await navigator.clipboard.writeText(text)
      msgSuccess('已复制到剪贴板')
      return true
    }
    // fallback
    const textarea = document.createElement('textarea')
    textarea.value = text
    textarea.style.position = 'fixed'
    textarea.style.opacity = '0'
    document.body.appendChild(textarea)
    textarea.select()
    const success = document.execCommand('copy')
    document.body.removeChild(textarea)
    if (success) msgSuccess('已复制到剪贴板')
    else msgError('复制失败')
    return success
  } catch (e) {
    msgError('复制失败')
    return false
  }
}

/* ========== 下载文件 ========== */

export function downloadFile(blob: Blob, filename: string) {
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  window.URL.revokeObjectURL(url)
}
