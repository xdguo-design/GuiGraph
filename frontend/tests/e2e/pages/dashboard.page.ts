import { Page, Locator } from '@playwright/test';
import { BasePage } from '../fixtures/base-page';

/**
 * 仪表盘页面对象模型
 */
export class DashboardPage extends BasePage {
  readonly urlPath = '/dashboard';

  readonly statCards: Locator;
  readonly totalChanges: Locator;
  readonly pendingApproval: Locator;
  readonly publishedCount: Locator;
  readonly rolledBackCount: Locator;
  readonly createChangeBtn: Locator;
  readonly orgStructureBtn: Locator;
  readonly emptyState: Locator;

  constructor(page: Page) {
    super(page);
    this.statCards = page.locator('.stat-card');
    this.totalChanges = page.locator('.stat-card').nth(0).locator('.stat-value');
    this.pendingApproval = page.locator('.stat-card').nth(1).locator('.stat-value');
    this.publishedCount = page.locator('.stat-card').nth(2).locator('.stat-value');
    this.rolledBackCount = page.locator('.stat-card').nth(3).locator('.stat-value');
    this.createChangeBtn = page.locator('button:has-text("新建变更")');
    this.orgStructureBtn = page.locator('button:has-text("组织架构")');
    this.emptyState = page.locator('.el-empty');
  }

  /**
   * 导航到仪表盘
   */
  async goto() {
    await super.goto(this.urlPath);
    await this.waitForLoad();
  }

  /**
   * 获取统计卡片值
   */
  async getStatValues(): Promise<{ total: string; pending: string; published: string; rolledBack: string }> {
    return {
      total: await this.totalChanges.textContent(),
      pending: await this.pendingApproval.textContent(),
      published: await this.publishedCount.textContent(),
      rolledBack: await this.rolledBackCount.textContent(),
    };
  }

  /**
   * 点击新建变更
   */
  async clickCreateChange() {
    await this.createChangeBtn.click();
  }

  /**
   * 点击组织架构
   */
  async clickOrgStructure() {
    await this.orgStructureBtn.click();
  }

  /**
   * 检查是否在仪表盘页
   */
  async isOnDashboard(): Promise<boolean> {
    await this.page.waitForURL(/\/dashboard/, { timeout: 5000 }).catch(() => {});
    return this.page.url().includes('/dashboard');
  }
}
