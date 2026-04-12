import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import puppeteer from 'puppeteer';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

describe('CPO Dashboard Integration', () => {
  let browser;
  let page;

  beforeAll(async () => {
    browser = await puppeteer.launch({
      headless: "new",
      // Bypass CORS so PapaParse can fetch local CSV from file:/// protocol
      args: ['--disable-web-security', '--allow-file-access-from-files']
    });
    page = await browser.newPage();
    const htmlPath = path.resolve(__dirname, '../../cpo_plays.html');
    await page.goto(`file:///${htmlPath.replace(/\\/g, '/')}`, { waitUntil: 'networkidle0' });
  });

  afterAll(async () => {
    await browser.close();
  });

  it('binds the CSV data correctly and updates the DOM', async () => {
    // Check if the Total Plays counter is > 100 (The ultimate goal)
    const totalCount = await page.$eval('#stat-total', el => parseInt(el.textContent));
    expect(totalCount).toBeGreaterThan(100);

    // Ensure rows rendered
    const rowCount = await page.$$eval('#tableBody tr', rows => rows.length);
    expect(rowCount).toEqual(totalCount);
  });

  it('filters by region correctly', async () => {
    // Click USA pill
    const usaButton = await page.$('div#regionFilters div.pill[data-filter="usa"]');
    await usaButton.click();
    
    // Short wait for UI to update
    await new Promise(r => setTimeout(r, 200));

    // USA plays count
    const usaCountActiveFilter = await page.$eval('#stat-total', el => parseInt(el.textContent));
    const statUsa = await page.$eval('#stat-usa', el => parseInt(el.textContent));
    
    // Total rows visible should equal the USA stat
    expect(usaCountActiveFilter).toEqual(statUsa);
  });

  it('filters by bucket (Moonshots) correctly', async () => {
    // Click Moonshot pill
    const moonButton = await page.$('div#bucketFilters div.pill[data-filter="Moonshot"]');
    await moonButton.click();
    
    await new Promise(r => setTimeout(r, 200));

    // Stats
    const totalCount = await page.$eval('#stat-total', el => parseInt(el.textContent));
    const moonCount = await page.$eval('#stat-moon', el => parseInt(el.textContent));
    expect(totalCount).toEqual(moonCount);
  });
  
  it('ensures no horizontal scrolling on standard desktop resolution', async () => {
    // Set viewport to a standard large desktop
    await page.setViewport({ width: 1440, height: 900 });
    
    // Evaluate if the body or any container is wider than the viewport
    const overflow = await page.evaluate(() => {
      const body = document.body;
      const html = document.documentElement;
      const width = window.innerWidth;
      
      return {
        bodyScrollWidth: body.scrollWidth,
        htmlScrollWidth: html.scrollWidth,
        windowInnerWidth: width,
        hasHorizontalScroll: (body.scrollWidth > width) || (html.scrollWidth > width)
      };
    });
    
    expect(overflow.hasHorizontalScroll).toBe(false);
  });
});
