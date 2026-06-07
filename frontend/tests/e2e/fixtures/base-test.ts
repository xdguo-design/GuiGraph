import { Page, expect, Locator } from '@playwright/test';

/**
 * 测试基类
 * 提供通用的测试辅助方法
 */
export class BaseTest {
  protected page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  /**
   * 获取元素定位器
   */
  protected locator(selector: string): Locator {
    return this.page.locator(selector);
  }

  /**
   * 获取元素文本
   */
  protected async getText(selector: string): Promise<string> {
    return await this.page.locator(selector).textContent();
  }

  /**
   * 点击元素
   */
  protected async click(selector: string): Promise<void> {
    await this.page.locator(selector).click();
  }

  /**
   * 填充输入框
   */
  protected async fill(selector: string, value: string): Promise<void> {
    await this.page.locator(selector).fill(value);
  }

  /**
   * 选择下拉选项
   */
  protected async select(selector: string, value: string): Promise<void> {
    await this.page.locator(selector).selectOption(value);
  }

  /**
   * 勾选复选框
   */
  protected async check(selector: string): Promise<void> {
    await this.page.locator(selector).check();
  }

  /**
   * 取消勾选复选框
   */
  protected async uncheck(selector: string): Promise<void> {
    await this.page.locator(selector).uncheck();
  }

  /**
   * 悬停在元素上
   */
  protected async hover(selector: string): Promise<void> {
    await this.page.locator(selector).hover();
  }

  /**
   * 双击元素
   */
  protected async dblclick(selector: string): Promise<void> {
    await this.page.locator(selector).dblclick();
  }

  /**
   * 等待元素可点击
   */
  protected async waitForClickable(selector: string, timeout?: number): Promise<void> {
    await this.page.locator(selector).waitFor({ state: 'visible', timeout });
  }

  /**
   * 断言元素存在
   */
  protected async expectExists(selector: string): Promise<void> {
    await expect(this.page.locator(selector)).toBeVisible();
  }

  /**
   * 断言元素不存在
   */
  protected async expectNotExists(selector: string): Promise<void> {
    await expect(this.page.locator(selector)).not.toBeVisible();
  }

  /**
   * 断言元素文本
   */
  protected async expectText(selector: string, expected: string | RegExp): Promise<void> {
    await expect(this.page.locator(selector)).toHaveText(expected);
  }

  /**
   * 断言元素包含文本
   */
  protected async expectContains(selector: string, text: string): Promise<void> {
    await expect(this.page.locator(selector)).toContainText(text);
  }

  /**
   * 断言输入框值
   */
  protected async expectInputValue(selector: string, value: string): Promise<void> {
    await expect(this.page.locator(selector)).toHaveValue(value);
  }

  /**
   * 断言元素可点击
   */
  protected async expectClickable(selector: string): Promise<void> {
    await expect(this.page.locator(selector)).toBeEnabled();
  }

  /**
   * 断言元素不可点击
   */
  protected async expectNotClickable(selector: string): Promise<void> {
    await expect(this.page.locator(selector)).toBeDisabled();
  }

  /**
   * 获取页面控制台消息
   */
  protected async getConsoleMessages(): Promise<string[]> {
    const messages: string[] = [];
    this.page.on('console', msg => {
      messages.push(msg.text());
    });
    return messages;
  }

  /**
   * 执行页面 JavaScript
   */
  protected async evaluate(fn: () => unknown): Promise<unknown> {
    return await this.page.evaluate(fn);
  }
}
