/**
 * 仪表盘功能 E2E 测试
 */
import { test, expect } from '@playwright/test';
import { LoginPage } from './pages/login.page';
import { DashboardPage } from './pages/dashboard.page';

test.describe('仪表盘 - 未登录访问', () => {
  test('未登录访问仪表盘应重定向到登录页', async ({ page }) => {
    await page.goto('/login');
    await page.evaluate(() => localStorage.removeItem('access_token'));

    await page.goto('/dashboard');
    await page.waitForURL(/\/login/, { timeout: 5000 });
    expect(page.url()).toContain('/login');
  });
});

test.describe('仪表盘 - 已登录访问', () => {
  test.beforeEach(async ({ page }) => {
    // 预设登录状态
    await page.goto('/login');
    await page.evaluate(() => {
      localStorage.setItem('access_token', 'test_token_for_dashboard');
    });
  });

  test('仪表盘页面应正确加载统计卡片', async ({ page }) => {
    const dashboard = new DashboardPage(page);
    await dashboard.goto();

    // 验证统计卡片存在
    await expect(dashboard.statCards).toHaveCount(4);
    await expect(dashboard.totalChanges).toBeVisible();
    await expect(dashboard.pendingApproval).toBeVisible();
    await expect(dashboard.publishedCount).toBeVisible();
    await expect(dashboard.rolledBackCount).toBeVisible();
  });

  test('统计卡片应显示初始值', async ({ page }) => {
    const dashboard = new DashboardPage(page);
    await dashboard.goto();

    const stats = await dashboard.getStatValues();
    expect(stats.total).toBe('0');
    expect(stats.pending).toBe('0');
    expect(stats.published).toBe('0');
    expect(stats.rolledBack).toBe('0');
  });

  test('应显示"最近变更"区域', async ({ page }) => {
    const dashboard = new DashboardPage(page);
    await dashboard.goto();

    // 验证最近变更区域
    await expect(page.locator('text=最近变更')).toBeVisible();
    await expect(dashboard.emptyState).toBeVisible();
  });

  test('应显示"快速操作"区域', async ({ page }) => {
    const dashboard = new DashboardPage(page);
    await dashboard.goto();

    // 验证快速操作按钮
    await expect(dashboard.createChangeBtn).toBeVisible();
    await expect(dashboard.orgStructureBtn).toBeVisible();
  });

  test('点击"新建变更"应跳转到创建页面', async ({ page }) => {
    const dashboard = new DashboardPage(page);
    await dashboard.goto();

    await dashboard.clickCreateChange();
    await page.waitForURL(/\/changes\/create/, { timeout: 5000 });
    expect(page.url()).toContain('/changes/create');
  });

  test('点击"组织架构"应跳转到组织管理页面', async ({ page }) => {
    const dashboard = new DashboardPage(page);
    await dashboard.goto();

    await dashboard.clickOrgStructure();
    await page.waitForURL(/\/org/, { timeout: 5000 });
    expect(page.url()).toContain('/org');
  });

  test('点击"查看全部"应跳转到变更列表', async ({ page }) => {
    const dashboard = new DashboardPage(page);
    await dashboard.goto();

    await page.locator('text=查看全部').click();
    await page.waitForURL(/\/changes/, { timeout: 5000 });
    expect(page.url()).toContain('/changes');
  });

  test('仪表盘页面标题应正确', async ({ page }) => {
    const dashboard = new DashboardPage(page);
    await dashboard.goto();

    const title = await dashboard.getTitle();
    expect(title).toContain('GuiGraph');
  });
});

test.describe('仪表盘 - 页面导航', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.evaluate(() => {
      localStorage.setItem('access_token', 'test_token_nav');
    });
  });

  test('页面刷新后应保持登录状态', async ({ page }) => {
    const dashboard = new DashboardPage(page);
    await dashboard.goto();

    // 刷新页面
    await dashboard.reload();
    await page.waitForLoadState('networkidle');

    // 验证仍停留在仪表盘（token 在 localStorage 中持久化）
    expect(page.url()).toContain('/dashboard');
    const token = await page.evaluate(() => localStorage.getItem('access_token'));
    expect(token).toBe('test_token_nav');
  });
});
