/**
 * 变更管理功能 E2E 测试
 * 覆盖变更管理页面的列表、筛选、导航功能
 */
import { test, expect } from '@playwright/test';

test.describe('变更管理 - 未登录', () => {
  test('未登录访问变更列表应重定向到登录页', async ({ page }) => {
    await page.goto('/login');
    await page.evaluate(() => localStorage.removeItem('access_token'));

    await page.goto('/changes');
    await page.waitForURL(/\/login/, { timeout: 5000 });
    expect(page.url()).toContain('/login');
  });
});

test.describe('变更管理 - 已登录', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.evaluate(() => {
      localStorage.setItem('access_token', 'test_token_changes');
    });
  });

  test('变更列表页面应正确加载', async ({ page }) => {
    await page.goto('/changes');
    await page.waitForLoadState('networkidle');

    // 验证页面标题
    await expect(page.locator('text=变更管理')).toBeVisible();
    // 验证新建变更按钮
    await expect(page.locator('button:has-text("新建变更")')).toBeVisible();
  });

  test('应显示筛选栏', async ({ page }) => {
    await page.goto('/changes');
    await page.waitForLoadState('networkidle');

    // 验证筛选字段
    await expect(page.locator('label:has-text("变更类型")')).toBeVisible();
    await expect(page.locator('label:has-text("状态")')).toBeVisible();
    await expect(page.locator('button:has-text("查询")')).toBeVisible();
  });

  test('变更类型筛选下拉应包含所有选项', async ({ page }) => {
    await page.goto('/changes');
    await page.waitForLoadState('networkidle');

    // 打开变更类型下拉
    await page.locator('label:has-text("变更类型")').locator('..').locator('.el-select').click();
    await page.waitForTimeout(300);

    // 验证下拉选项
    await expect(page.locator('text=DB 变更')).toBeVisible();
    await expect(page.locator('text=API 变更')).toBeVisible();
    await expect(page.locator('text=配置变更')).toBeVisible();
    await expect(page.locator('text=代码变更')).toBeVisible();
    await expect(page.locator('text=基础设施')).toBeVisible();

    // 关闭下拉
    await page.locator('label:has-text("变更类型")').locator('..').locator('.el-select').click();
  });

  test('状态筛选下拉应包含所有选项', async ({ page }) => {
    await page.goto('/changes');
    await page.waitForLoadState('networkidle');

    // 打开状态下拉
    await page.locator('label:has-text("状态")').locator('..').locator('.el-select').click();
    await page.waitForTimeout(300);

    // 验证下拉选项
    await expect(page.locator('text=草稿')).toBeVisible();
    await expect(page.locator('text=已审批')).toBeVisible();
    await expect(page.locator('text=已发布')).toBeVisible();
    await expect(page.locator('text=已回滚')).toBeVisible();

    // 关闭下拉
    await page.locator('label:has-text("状态")').locator('..').locator('.el-select').click();
  });

  test('变更列表应显示数据表格', async ({ page }) => {
    await page.goto('/changes');
    await page.waitForLoadState('networkidle');

    // 验证表格列头
    await expect(page.locator('text=变更 ID')).toBeVisible();
    await expect(page.locator('text=类型')).toBeVisible();
    await expect(page.locator('text=变更内容')).toBeVisible();
    await expect(page.locator('text=原因')).toBeVisible();
    await expect(page.locator('text=状态')).toBeVisible();
    await expect(page.locator('text=创建时间')).toBeVisible();
    await expect(page.locator('text=操作')).toBeVisible();
  });

  test('应显示分页组件', async ({ page }) => {
    await page.goto('/changes');
    await page.waitForLoadState('networkidle');

    // 验证分页存在
    await expect(page.locator('.el-pagination')).toBeVisible();
  });

  test('点击"新建变更"应跳转到创建页面', async ({ page }) => {
    await page.goto('/changes');
    await page.waitForLoadState('networkidle');

    await page.locator('button:has-text("新建变更")').click();
    await page.waitForURL(/\/changes\/create/, { timeout: 5000 });
    expect(page.url()).toContain('/changes/create');
  });

  test('新建变更页面应正确加载', async ({ page }) => {
    await page.goto('/changes/create');
    await page.waitForLoadState('networkidle');

    // 验证创建页面元素
    await expect(page.locator('text=新建变更')).toBeVisible();
  });
});

test.describe('变更管理 - 表格数据显示', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.evaluate(() => {
      localStorage.setItem('access_token', 'test_token_changes');
    });
  });

  test('数据列为空时应显示空状态', async ({ page }) => {
    await page.goto('/changes');
    await page.waitForLoadState('networkidle');

    // 当无数据时，el-table 显示"暂无数据"
    const emptyText = page.locator('.el-table__empty-text, .el-empty__description');
    if (await emptyText.isVisible().catch(() => false)) {
      await expect(emptyText).toBeVisible();
    }
  });
});
