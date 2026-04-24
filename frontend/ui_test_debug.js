const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();
  
  await page.goto('http://localhost:3000/upload');
  await page.waitForLoadState('networkidle');
  await page.screenshot({ path: 'upload_page_initial.png', fullPage: true });

  const html = await page.content();
  const fs = require('fs');
  fs.writeFileSync('page.html', html);
  
  await browser.close();
})();
