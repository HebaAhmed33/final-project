const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();
  
  // 1. Navigate to upload
  await page.goto('http://localhost:3000/upload');
  await page.waitForLoadState('networkidle');
  
  // 1b. Check if we are on login page
  const isLogin = await page.$('h1.login-title');
  if (isLogin) {
    await page.fill('#login-email', 'demo@smartisms.com');
    await page.fill('#login-password', 'demo123');
    await page.click('button[type="submit"]');
    await page.waitForLoadState('networkidle');
    await page.goto('http://localhost:3000/upload');
    await page.waitForLoadState('networkidle');
  }
  
  // 3. Fill the form
  await page.fill('input[placeholder="e.g. Q3 Risk Audit"]', 'Aegis_One_Company_Template_Filled test');
  
  // 4. Set the file
  const filePath = path.resolve('c:\\new project\\backend\\Aegis_One_Company_Template_Filled.xlsx');
  await page.setInputFiles('#assessment-file-input', filePath);
  
  // 5. Submit
  await page.click('button[type="submit"].btn-primary');
  
  // Wait a bit
  await page.waitForTimeout(5000);
  
  // 6. Wait for the results to appear
  await page.waitForSelector('text=Assessment Results', { timeout: 30000 });
  await page.waitForTimeout(2000);
  
  // 7. Grab the text of the score cards
  const cards = await page.$$eval('.card', elements => elements.map(el => el.innerText));
  console.log("=== UI RESULTS ===");
  cards.forEach(c => console.log(c.replace(/\n/g, ' | ')));
  console.log("==================");
  
  await page.screenshot({ path: 'ui_results_new_template.png', fullPage: true });
  
  await browser.close();
})();
