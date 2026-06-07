import { Page, Locator } from '@playwright/test';
import { BasePage } from '../fixtures/base-page';

/**
 * 登录页面对象模型
 */
export class LoginPage extends BasePage {
  readonly urlPath = '/login';

  // 页面元素定位
  readonly usernameInput: Locator;
  readonly passwordInput: Locator;
  readonly loginButton: Locator;
  readonly wechatButton: Locator;
  readonly formTitle: Locator;
  readonly errorMessage: Locator;

  constructor(page: Page) {
    super(page);
    this.usernameInput = page.locator('input[placeholder="用户名/邮箱/手机"]');
    this.passwordInput = page.locator('input[placeholder="密码"]');
    this.loginButton = page.locator('button:has-text("登录")');
    this.wechatButton = page.locator('button:has-text("微信扫码登录")');
    this.formTitle = page.locator('.login-box h1');
    this.errorMessage = page.locator('.el-message--error');
  }

  /**
   * 导航到登录页
   */
  async goto() {
    await super.goto(this.urlPath);
    await this.waitForLoad();
  }

  /**
   * 执行登录操作
   * @param username 用户名
   * @param password 密码
   */
  async login(username: string, password: string) {
    await this.usernameInput.fill(username);
    await this.passwordInput.fill(password);
    await this.loginButton.click();
  }

  /**
   * 检查表单验证错误
   */
  async getFormValidationErrors(): Promise<string[]> {
    const errors: string[] = [];
    const errorElements = await this.page.locator('.el-form-item__error').all();
    for (const el of errorElements) {
      errors.push(await el.textContent());
    }
    return errors;
  }

  /**
   * 检查是否在登录页
   */
  async isOnLoginPage(): Promise<boolean> {
    await this.page.waitForURL(/\/login/, { timeout: 5000 }).catch(() => {});
    return this.page.url().includes('/login');
  }

  /**
   * 检查是否已登录（token 存在 localStorage）
   */
  async isLoggedIn(): Promise<boolean> {
    const token = await this.page.evaluate(() => localStorage.getItem('access_token'));
    return token !== null && token !== '';
  }

  /**
   * 清除登录状态
   */
  async clearLoginState() {
    await this.page.evaluate(() => localStorage.removeItem('access_token'));
  }
}
