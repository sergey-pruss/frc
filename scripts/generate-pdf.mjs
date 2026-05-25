#!/usr/bin/env node
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import puppeteer from "puppeteer";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(__dirname, "..");

const footerHtml = `
<div style="width:100%; font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif; font-size: 8px; color: #999; display: flex; justify-content: space-between; padding: 0 6mm;">
  <span></span>
  <span>Serenity</span>
  <span><span class="pageNumber"></span> / <span class="totalPages"></span></span>
</div>`;

const reports = [
  {
    src: resolve(ROOT, "export/seo-report-print.html"),
    dst: resolve(ROOT, "export/seo-strategy-report.pdf"),
    name: "SEO Strategy",
  },
  {
    src: resolve(ROOT, "analysis/index.html"),
    dst: resolve(ROOT, "export/competitor-analysis-report.pdf"),
    name: "Competitor Analysis",
  },
];

const browser = await puppeteer.launch({ headless: true });

for (const { src, dst, name } of reports) {
  const page = await browser.newPage();
  await page.goto(`file://${src}`, { waitUntil: "networkidle0" });
  await page.pdf({
    path: dst,
    format: "A4",
    landscape: true,
    margin: { top: "16mm", bottom: "20mm", left: "14mm", right: "14mm" },
    printBackground: true,
    displayHeaderFooter: true,
    headerTemplate: '<span></span>',
    footerTemplate: footerHtml,
  });
  await page.close();
  console.log(`pdf → ${dst} (${name})`);
}

await browser.close();
