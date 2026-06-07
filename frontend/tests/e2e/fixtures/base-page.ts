import { Page, Locator, expect } from '@playwright/test';
import { BaseTest } from './base-test';

/**
 * 页面对象模型 (Page Object Model) 基类
 * 
 * 所有页面类都应继承此基类，提供统一的页面操作和断言方法
 */
export class BasePage extends BaseTest {
  readonly page: Page;

  constructor(page: Page) {
    super(page);
    this.page = page;
  }

  /**
   * 导航到页面
   */
  async goto(path: string): Promise<void> {
    await this.page.goto(path);
  }

  /**
   * 等待页面加载完成
   */
  async waitForLoad(): Promise<void> {
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * 获取页面标题
   */
  async getTitle(): Promise<string> {
    return await this.page.title();
  }

  /**
   * 获取当前 URL
   */
  async getCurrentUrl(): Promise<string> {
    return this.page.url();
  }

  /**
   * 刷新页面
   */
  async reload(): Promise<void> {
    await this.page.reload();
  }

  /**
   * 截图
   */
  async takeScreenshot(name: string): Promise<void> {
    await this.page.screenshot({ 
      path: `test-results/${name}.png`,
      fullPage: true 
    });
  }

  /**
   * 等待元素可见
   */
  async waitForVisible(selector: string, timeout?: number): Promise<void> {
    await this.page.waitForSelector(selector, { 
      state: 'visible', 
      timeout 
    });
  }

  /**
   * 等待元素隐藏
   */
  async waitForHidden(selector: string, timeout?: number): Promise<void> {
    await this.page.waitForSelector(selector, { 
      state: 'hidden', 
      timeout 
    });
  }

  /**
   * 等待导航完成
   */
  async waitForNavigation(options?: { url?: string | RegExp; timeout?: number }): Promise<void> {
    await this.page.waitForNavigation(options);
  }

  /**
   * 检查 URL 是否包含指定文本
   */
  async expectUrlContains(text: string | RegExp): Promise<void> {
    await expect(this.page).toHaveURL(/.*text.*/);
  }

  /**
   * 检查页面是否包含文本
   */
  async expectPageContains(text: string): Promise<void> {
    await expect(this.page).toContainText(text);
  }
}
