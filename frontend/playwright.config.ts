import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright E2E 测试配置
 * 
 * 支持 Chrome、Chromium、Firefox、WebKit 等多种浏览器
 * 使用 Chrome 进行测试: npx playwright test --project=chromium
 */
export default defineConfig({
  // 测试目录
  testDir: './tests/e2e',
  
  // 测试文件匹配模式
  testMatch: '**/*.spec.ts',
  
  // 输出目录
  outputDir: './test-results/',
  
  // 失败重试次数
  retries: process.env.CI ? 2 : 0,
  
  // 并行执行
  workers: process.env.CI ? 1 : undefined,
  
  // 报告器
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['list'],
    ...(process.env.CI ? [['github'] as any] : []),
  ],
  
  // 使用基地址（前端开发服务器）
  use: {
    baseURL: 'http://localhost:10010',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  
  // 浏览器配置
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'chrome',
      use: {
        ...devices['Desktop Chrome'],
        channel: 'chrome', // 使用已安装的 Chrome 浏览器
      },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    
    // 移动端测试
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
    
    // 有头模式（可见浏览器）- 用于调试
    {
      name: 'chromium-headed',
      use: { ...devices['Desktop Chrome'], headless: false },
    },
  ],
  
  // 开发服务器（可选，测试前自动启动）
  // webServer: {
  //   command: 'npm run dev',
  //   url: 'http://localhost:10010',
  //   reuseExistingServer: !process.env.CI,
  // },
});
