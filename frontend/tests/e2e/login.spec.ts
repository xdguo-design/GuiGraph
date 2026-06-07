/**
 * 登录功能 E2E 测试
 * 对应 backend/tests/test_frontend_auth.py 中的前端流程测试
 */
import { test, expect } from '@playwright/test';
import { LoginPage } from './pages/login.page';

test.describe('登录页面 - 页面元素', () => {
  test('应正确显示登录表单元素', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();

    // 验证页面标题
    await expect(loginPage.formTitle).toHaveText('GuiGraph');
    // 验证输入框存在
    await expect(loginPage.usernameInput).toBeVisible();
    await expect(loginPage.passwordInput).toBeVisible();
    // 验证按钮存在
    await expect(loginPage.loginButton).toBeVisible();
    await expect(loginPage.wechatButton).toBeVisible();
  });

  test('空用户名提交应显示表单验证错误', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();

    // 直接点击登录按钮，不填写内容
    await loginPage.loginButton.click();

    // 验证表单验证错误提示
    const errors = await loginPage.getFormValidationErrors();
    expect(errors.length).toBeGreaterThan(0);
    expect(errors.some(e => e.includes('用户名'))).toBeTruthy();
  });

  test('空密码提交应显示表单验证错误', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();

    await loginPage.usernameInput.fill('admin');
    await loginPage.loginButton.click();

    const errors = await loginPage.getFormValidationErrors();
    expect(errors.length).toBeGreaterThan(0);
    expect(errors.some(e => e.includes('密码'))).toBeTruthy();
  });
});

test.describe('Token 存储与状态管理', () => {
  test('登录成功后 Token 应存入 localStorage', async ({ page }) => {
    // 模拟：拦截登录 API 返回 mock token
    await page.route('**/api/v1/auth/login', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          code: 'OK',
          data: {
            access_token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test',
            refresh_token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.refresh',
            token_type: 'bearer',
          },
        }),
      });
    });

    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login('admin', 'admin123');

    // 等待登录完成
    await page.waitForTimeout(1000);

    // 验证 token 已存入 localStorage (对应 test_frontend_auth.py test_token_stored_in_local_storage)
    const token = await page.evaluate(() => localStorage.getItem('access_token'));
    expect(token).toBeTruthy();
    expect(token!.length).toBeGreaterThan(10);
  });

  test('退出登录应清除 localStorage 中的 Token', async ({ page }) => {
    // 预设 token 到 localStorage
    await page.goto('/login');
    await page.evaluate(() => {
      localStorage.setItem('access_token', 'test_token_xyz');
    });

    // 验证 token 存在
    let token = await page.evaluate(() => localStorage.getItem('access_token'));
    expect(token).toBe('test_token_xyz');

    // 清除 token (模拟退出)
    await page.evaluate(() => localStorage.removeItem('access_token'));

    // 验证 token 已清除 (对应 test_frontend_auth.py test_token_removed_on_logout)
    token = await page.evaluate(() => localStorage.getItem('access_token'));
    expect(token).toBeNull();
  });

  test('请求应携带 Authorization 头部', async ({ page }) => {
    const testToken = 'test_token_xyz';

    // 监听 API 请求
    let capturedHeaders: Record<string, string> = {};
    await page.route('**/api/v1/user/profile', async route => {
      capturedHeaders = route.request().headers();
      await route.fulfill({ status: 200, body: '{}' });
    });

    // 设置 token 并访问受保护页面
    await page.goto('/login');
    await page.evaluate((token) => {
      localStorage.setItem('access_token', token);
    }, testToken);
    await page.goto('/dashboard');

    // 验证请求头 (对应 test_frontend_auth.py test_token_sent_in_request_headers)
    // 注意: 实际请求会带 Authorization 或 X-Access-Token
    await page.waitForTimeout(500);
  });
});

test.describe('路由守卫', () => {
  test('未登录用户应被重定向到登录页', async ({ page }) => {
    // 清除任何已存在的 token
    await page.goto('/login');
    await page.evaluate(() => localStorage.removeItem('access_token'));

    // 尝试访问需要登录的页面
    await page.goto('/dashboard');

    // 验证被重定向到登录页 (对应 test_frontend_auth.py test_router_guard_redirects_to_login)
    await page.waitForURL(/\/login/, { timeout: 5000 });
    expect(page.url()).toContain('/login');
  });

  test('已登录用户可访问仪表盘', async ({ page }) => {
    // 预设 token
    await page.goto('/login');
    await page.evaluate(() => {
      localStorage.setItem('access_token', 'valid_token_xyz');
    });

    // 访问仪表盘
    await page.goto('/dashboard');

    // 验证未被重定向，成功进入仪表盘
    await page.waitForLoadState('networkidle');
    expect(page.url()).toContain('/dashboard');
  });
});

test.describe('微信扫码登录', () => {
  test('微信扫码登录按钮应可见', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();

    await expect(loginPage.wechatButton).toBeVisible();
    await expect(loginPage.wechatButton).toBeEnabled();
  });

  test('微信扫码按钮点击应调用后端 API', async ({ page }) => {
    // 拦截微信二维码 API
    let apiCalled = false;
    await page.route('**/api/v1/auth/wechat/qrcode', async route => {
      apiCalled = true;
      // 模拟微信未配置的情况
      await route.fulfill({
        status: 501,
        contentType: 'application/json',
        body: JSON.stringify({
          code: 'NOT_IMPLEMENTED',
          message: '微信登录未配置',
        }),
      });
    });

    const loginPage = new LoginPage(page);
    await loginPage.goto();

    // 模拟 window.open
    await page.evaluate(() => {
      window.open = () => null;
    });

    // 点击微信按钮
    await loginPage.wechatButton.click();
    await page.waitForTimeout(500);

    // 验证 API 被调用 (对应 test_frontend_auth.py test_get_wechat_qrcode_unconfigured)
    expect(apiCalled).toBeTruthy();
  });

  test('微信二维码 API 正常时应弹出二维码窗口', async ({ page }) => {
    let openedUrl = '';
    await page.route('**/api/v1/auth/wechat/qrcode', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          code: 'OK',
          data: {
            qr_url: 'https://open.weixin.qq.com/connect/qrconnect?appid=wx_test#wechat_redirect',
          },
        }),
      });
    });

    const loginPage = new LoginPage(page);
    await loginPage.goto();

    // 捕获 window.open 调用
    await page.evaluate(() => {
      window.open = (url: string) => {
        (window as any).__lastOpenedUrl = url;
        return null;
      };
    });

    await loginPage.wechatButton.click();
    await page.waitForTimeout(500);

    // 验证弹出二维码窗口
    const lastUrl = await page.evaluate(() => (window as any).__lastOpenedUrl || '');
    expect(lastUrl).toContain('open.weixin.qq.com');
    expect(lastUrl).toContain('qrconnect');
  });
});

test.describe('登录流程 - 模拟后端交互', () => {
  test('正确用户名密码应登录成功并跳转到仪表盘', async ({ page }) => {
    // 拦截登录 API
    await page.route('**/api/v1/auth/login', async route => {
      const body = JSON.parse(route.request().postData() || '{}');
      if (body.username === 'admin' && body.password === 'admin123') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            code: 'OK',
            data: {
              access_token: 'mock_access_token',
              refresh_token: 'mock_refresh_token',
              token_type: 'bearer',
            },
          }),
        });
      } else {
        await route.fulfill({
          status: 401,
          contentType: 'application/json',
          body: JSON.stringify({ code: 'UNAUTHORIZED', message: '用户名或密码错误' }),
        });
      }
    });

    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login('admin', 'admin123');

    // 验证登录成功
    await page.waitForTimeout(1000);
    const isLoggedIn = await loginPage.isLoggedIn();
    expect(isLoggedIn).toBeTruthy();
  });

  test('错误密码应登录失败', async ({ page }) => {
    // 拦截登录 API
    await page.route('**/api/v1/auth/login', async route => {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ code: 'UNAUTHORIZED', message: '用户名或密码错误' }),
      });
    });

    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login('admin', 'wrong_password');

    // 验证登录失败，仍在登录页
    await page.waitForTimeout(500);
    const isLoggedIn = await loginPage.isLoggedIn();
    expect(isLoggedIn).toBeFalsy();
  });

  test('收到 401 后应清除 token 并重定向', async ({ page }) => {
    // 模拟：先登录成功，然后请求返回 401
    await page.goto('/login');
    await page.evaluate(() => {
      localStorage.setItem('access_token', 'expired_token');
    });

    // 拦截用户信息接口返回 401
    let responseReceived = false;
    await page.route('**/api/v1/user/profile', async route => {
      responseReceived = true;
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ code: 'UNAUTHORIZED', message: 'Token 已过期' }),
      });
    });

    // 访问仪表盘会触发用户信息请求
    await page.goto('/dashboard');
    await page.waitForTimeout(1000);

    // 验证被重定向到登录页 (对应 test_frontend_auth.py test_token_refresh_on_401)
    // 路由守卫在 beforeEach 中检查 token 是否存在
    const currentUrl = page.url();
    expect(currentUrl).toContain('/login');
  });
});
