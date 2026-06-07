const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ headless: true });
  // Tablet
  let page = await browser.newPage();
  await page.setViewport({ width: 768, height: 1024 });
  await page.goto('http://localhost:10010/kanban', { waitUntil: 'networkidle2' });
  await new Promise(r => setTimeout(r, 3000));
  // Set auth
  await page.evaluate(() => {
    const t = localStorage.getItem('access_token');
    return t ? 'has token' : 'no token';
  });
  await page.screenshot({ path: 'test-screenshots/gantt-tablet-768.png' });
  console.log('Tablet screenshot saved');

  // Mobile
  await page.setViewport({ width: 375, height: 667 });
  await page.reload({ waitUntil: 'networkidle2' });
  await new Promise(r => setTimeout(r, 3000));
  await page.screenshot({ path: 'test-screenshots/gantt-mobile-375.png' });
  console.log('Mobile screenshot saved');

  await browser.close();
  console.log('Done');
})();
